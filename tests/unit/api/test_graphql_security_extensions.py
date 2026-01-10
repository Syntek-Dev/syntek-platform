"""Comprehensive unit tests for GraphQL security extensions.

Tests cover:
- Query depth limiting (prevent deeply nested queries)
- Query complexity analysis (prevent expensive queries)
- Introspection control (disable in production)
- Edge cases and boundary conditions
- Configuration and customization

These extensions protect against malicious or resource-intensive GraphQL queries.

Following TDD approach: tests written before full implementation.
"""

from unittest.mock import Mock, patch

from django.conf import settings

import pytest

from api.security import (
    IntrospectionControlExtension,
    QueryComplexityLimitExtension,
    QueryDepthLimitExtension,
)


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.graphql
class TestQueryDepthLimitExtension:
    """Comprehensive tests for query depth limiting."""

    @pytest.fixture
    def mock_execution_context(self) -> Mock:
        """Provide mock GraphQL execution context.

        Returns:
            Mock ExecutionContext with graphql_document
        """
        context = Mock()
        context.query = "query { user { posts { comments { author { name } } } } }"
        return context

    @pytest.fixture
    def simple_query_document(self) -> Mock:
        """Provide simple query document (depth 1).

        Returns:
            Mock document with single level query
        """
        document = Mock(spec=['definitions'])
        definition = Mock(spec=['selection_set'])
        selection = Mock(spec=['selection_set'])

        # query { me { id } } - depth 1
        selection.selection_set = None
        definition.selection_set = Mock(spec=['selections'], selections=[selection])
        document.definitions = [definition]

        return document

    @pytest.fixture
    def nested_query_document(self) -> Mock:
        """Provide deeply nested query document.

        Returns:
            Mock document with 5-level nested query
        """
        document = Mock(spec=['definitions'])
        definition = Mock(spec=['selection_set'])

        # Create nested structure: level1 -> level2 -> level3 -> level4 -> level5
        level5 = Mock(spec=['selection_set'])
        level5.selection_set = None

        level4 = Mock(spec=['selection_set'])
        level4.selection_set = Mock(spec=['selections'], selections=[level5])

        level3 = Mock(spec=['selection_set'])
        level3.selection_set = Mock(spec=['selections'], selections=[level4])

        level2 = Mock(spec=['selection_set'])
        level2.selection_set = Mock(spec=['selections'], selections=[level3])

        level1 = Mock(spec=['selection_set'])
        level1.selection_set = Mock(spec=['selections'], selections=[level2])

        definition.selection_set = Mock(spec=['selections'], selections=[level1])
        document.definitions = [definition]

        return document

    def test_extension_initializes_with_default_max_depth(self, mock_execution_context) -> None:
        """Test extension initializes with default max depth.

        Given: No max_depth parameter provided
        When: Extension is initialized
        Then: max_depth is set to 10 (default)
        """
        extension = QueryDepthLimitExtension(execution_context=mock_execution_context)

        assert extension.max_depth == 10

    def test_extension_initializes_with_custom_max_depth(self, mock_execution_context) -> None:
        """Test extension accepts custom max depth.

        Given: max_depth=5 parameter
        When: Extension is initialized
        Then: max_depth is set to 5
        """
        extension = QueryDepthLimitExtension(execution_context=mock_execution_context, max_depth=5)

        assert extension.max_depth == 5

    @patch.object(settings, "GRAPHQL_MAX_QUERY_DEPTH", 15)
    def test_extension_uses_settings_max_depth(self, mock_execution_context) -> None:
        """Test extension uses GRAPHQL_MAX_QUERY_DEPTH from settings.

        Given: GRAPHQL_MAX_QUERY_DEPTH=15 in settings
        When: Extension is initialized without max_depth parameter
        Then: max_depth is set to 15 from settings
        """
        extension = QueryDepthLimitExtension(execution_context=mock_execution_context)

        # Should use settings value if no parameter provided
        assert extension.max_depth == 15

    def test_simple_query_passes_depth_check(
        self, mock_execution_context, simple_query_document
    ) -> None:
        """Test simple query passes depth limit.

        Given: Query with depth 1, max_depth 10
        When: on_execute() is called
        Then: Query is allowed (no exception)
        """
        mock_execution_context.graphql_document = simple_query_document
        extension = QueryDepthLimitExtension(execution_context=mock_execution_context, max_depth=10)

        # Should not raise exception
        generator = extension.on_execute()
        next(generator, None)

    def test_deeply_nested_query_exceeds_depth_limit(
        self, mock_execution_context, nested_query_document
    ) -> None:
        """Test deeply nested query exceeds depth limit.

        Given: Query with depth 5, max_depth 3
        When: on_execute() is called
        Then: Exception is raised
        """
        mock_execution_context.graphql_document = nested_query_document
        extension = QueryDepthLimitExtension(execution_context=mock_execution_context, max_depth=3)

        # Should raise exception for depth > 3
        with pytest.raises(Exception) as exc_info:
            generator = extension.on_execute()
            next(generator)

        assert "depth" in str(exc_info.value).lower()
        assert "exceeds" in str(exc_info.value).lower()

    def test_query_at_exact_max_depth_is_allowed(
        self, mock_execution_context, nested_query_document
    ) -> None:
        """Test query at exact max depth is allowed.

        Given: Query with depth 5, max_depth 5
        When: on_execute() is called
        Then: Query is allowed
        """
        mock_execution_context.graphql_document = nested_query_document
        extension = QueryDepthLimitExtension(execution_context=mock_execution_context, max_depth=5)

        # Should not raise exception (depth == max_depth)
        generator = extension.on_execute()
        next(generator, None)

    def test_calculate_query_depth_handles_empty_document(self, mock_execution_context) -> None:
        """Test depth calculation handles empty document.

        Given: Empty/None document
        When: _calculate_query_depth() is called
        Then: Returns 0
        """
        extension = QueryDepthLimitExtension(execution_context=mock_execution_context)

        depth = extension._calculate_query_depth(None)
        assert depth == 0

    def test_calculate_query_depth_handles_no_selections(self, mock_execution_context) -> None:
        """Test depth calculation handles document with no selections.

        Given: Document with no selection_set
        When: _calculate_query_depth() is called
        Then: Returns depth 0
        """
        document = Mock()
        document.definitions = []

        extension = QueryDepthLimitExtension(execution_context=mock_execution_context)
        depth = extension._calculate_query_depth(document)

        assert depth == 0

    def test_depth_calculation_with_multiple_definitions(self, mock_execution_context) -> None:
        """Test depth calculation with multiple query definitions.

        Given: Document with multiple definitions of different depths
        When: _calculate_query_depth() is called
        Then: Returns maximum depth across all definitions
        """
        # Definition 1: depth 2
        def1_level2 = Mock(spec=['selection_set'])
        def1_level2.selection_set = None
        def1_level1 = Mock(spec=['selection_set'])
        def1_level1.selection_set = Mock(spec=['selections'], selections=[def1_level2])
        def1 = Mock(spec=['selection_set'])
        def1.selection_set = Mock(spec=['selections'], selections=[def1_level1])

        # Definition 2: depth 4 (deeper)
        def2_level4 = Mock(spec=['selection_set'])
        def2_level4.selection_set = None
        def2_level3 = Mock(spec=['selection_set'])
        def2_level3.selection_set = Mock(spec=['selections'], selections=[def2_level4])
        def2_level2 = Mock(spec=['selection_set'])
        def2_level2.selection_set = Mock(spec=['selections'], selections=[def2_level3])
        def2_level1 = Mock(spec=['selection_set'])
        def2_level1.selection_set = Mock(spec=['selections'], selections=[def2_level2])
        def2 = Mock(spec=['selection_set'])
        def2.selection_set = Mock(spec=['selections'], selections=[def2_level1])

        document = Mock(spec=['definitions'])
        document.definitions = [def1, def2]

        extension = QueryDepthLimitExtension(execution_context=mock_execution_context)
        depth = extension._calculate_query_depth(document)

        # Should return maximum depth (4)
        assert depth == 4

    def test_depth_limit_error_message_includes_details(
        self, mock_execution_context, nested_query_document
    ) -> None:
        """Test error message includes depth details.

        Given: Query exceeding depth limit
        When: Exception is raised
        Then: Error message includes actual depth and max depth
        """
        mock_execution_context.graphql_document = nested_query_document
        extension = QueryDepthLimitExtension(execution_context=mock_execution_context, max_depth=2)

        with pytest.raises(Exception) as exc_info:
            generator = extension.on_execute()
            next(generator)

        error_message = str(exc_info.value)
        assert "2" in error_message  # max_depth
        assert "depth" in error_message.lower()


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.graphql
class TestQueryComplexityLimitExtension:
    """Comprehensive tests for query complexity limiting."""

    @pytest.fixture
    def mock_execution_context(self) -> Mock:
        """Provide mock GraphQL execution context.

        Returns:
            Mock ExecutionContext
        """
        context = Mock()
        context.query = "query { users { id name posts { title } } }"
        return context

    @pytest.fixture
    def simple_query_document(self) -> Mock:
        """Provide simple query document (low complexity).

        Returns:
            Mock document with 2 fields
        """
        document = Mock(spec=['definitions'])
        definition = Mock(spec=['selection_set'])

        # query { me { id } } - complexity: 1 (me) + 1 (id) = 2
        field_id = Mock(spec=['name', 'selection_set'])
        field_id.name = Mock(value="id")
        field_id.selection_set = None

        field_me = Mock(spec=['name', 'selection_set'])
        field_me.name = Mock(value="me")
        field_me.selection_set = Mock(spec=['selections'], selections=[field_id])

        definition.selection_set = Mock(spec=['selections'], selections=[field_me])
        document.definitions = [definition]

        return document

    @pytest.fixture
    def complex_list_query_document(self) -> Mock:
        """Provide query with list fields (high complexity).

        Returns:
            Mock document with list field
        """
        document = Mock(spec=['definitions'])
        definition = Mock(spec=['selection_set'])

        # query { users { posts { comments } } }
        # users is list field (10x multiplier)
        # posts is list field (10x multiplier)
        # comments is list field (10x multiplier)
        # complexity: 1 * 10 (users) * 10 (posts) * 10 (comments) = 1000

        field_comments = Mock(spec=['name', 'selection_set'])
        field_comments.name = Mock(value="comments")  # List field (plural)
        field_comments.selection_set = None

        field_posts = Mock(spec=['name', 'selection_set'])
        field_posts.name = Mock(value="posts")  # List field (plural)
        field_posts.selection_set = Mock(spec=['selections'], selections=[field_comments])

        field_users = Mock(spec=['name', 'selection_set'])
        field_users.name = Mock(value="users")  # List field (plural)
        field_users.selection_set = Mock(spec=['selections'], selections=[field_posts])

        definition.selection_set = Mock(spec=['selections'], selections=[field_users])
        document.definitions = [definition]

        return document

    def test_extension_initializes_with_default_max_complexity(
        self, mock_execution_context
    ) -> None:
        """Test extension initializes with default max complexity.

        Given: No max_complexity parameter provided
        When: Extension is initialized
        Then: max_complexity is set to 1000 (default)
        """
        extension = QueryComplexityLimitExtension(execution_context=mock_execution_context)

        assert extension.max_complexity == 1000

    def test_extension_initializes_with_custom_max_complexity(self, mock_execution_context) -> None:
        """Test extension accepts custom max complexity.

        Given: max_complexity=500 parameter
        When: Extension is initialized
        Then: max_complexity is set to 500
        """
        extension = QueryComplexityLimitExtension(
            execution_context=mock_execution_context, max_complexity=500
        )

        assert extension.max_complexity == 500

    @patch.object(settings, "GRAPHQL_MAX_QUERY_COMPLEXITY", 2000)
    def test_extension_uses_settings_max_complexity(self, mock_execution_context) -> None:
        """Test extension uses GRAPHQL_MAX_QUERY_COMPLEXITY from settings.

        Given: GRAPHQL_MAX_QUERY_COMPLEXITY=2000 in settings
        When: Extension is initialized without max_complexity parameter
        Then: max_complexity is set to 2000 from settings
        """
        extension = QueryComplexityLimitExtension(execution_context=mock_execution_context)

        assert extension.max_complexity == 2000

    def test_simple_query_passes_complexity_check(
        self, mock_execution_context, simple_query_document
    ) -> None:
        """Test simple query passes complexity limit.

        Given: Query with low complexity, max_complexity 1000
        When: on_execute() is called
        Then: Query is allowed
        """
        mock_execution_context.graphql_document = simple_query_document
        extension = QueryComplexityLimitExtension(
            execution_context=mock_execution_context, max_complexity=1000
        )

        # Should not raise exception
        generator = extension.on_execute()
        next(generator, None)

    def test_complex_query_exceeds_complexity_limit(
        self, mock_execution_context, complex_list_query_document
    ) -> None:
        """Test complex query exceeds complexity limit.

        Given: Query with high complexity, max_complexity 100
        When: on_execute() is called
        Then: Exception is raised
        """
        mock_execution_context.graphql_document = complex_list_query_document
        extension = QueryComplexityLimitExtension(
            execution_context=mock_execution_context, max_complexity=100
        )

        # Should raise exception for complexity > 100
        with pytest.raises(Exception) as exc_info:
            generator = extension.on_execute()
            next(generator)

        assert "complexity" in str(exc_info.value).lower()
        assert "exceeds" in str(exc_info.value).lower()

    def test_query_at_exact_max_complexity_is_allowed(
        self, mock_execution_context, simple_query_document
    ) -> None:
        """Test query at exact max complexity is allowed.

        Given: Query with complexity exactly at limit
        When: on_execute() is called
        Then: Query is allowed
        """
        mock_execution_context.graphql_document = simple_query_document
        # Calculate actual complexity first
        extension = QueryComplexityLimitExtension(
            execution_context=mock_execution_context, max_complexity=10000
        )
        actual_complexity = extension._calculate_query_complexity(simple_query_document)

        # Set max to actual complexity
        extension2 = QueryComplexityLimitExtension(
            execution_context=mock_execution_context, max_complexity=actual_complexity
        )

        # Should not raise exception
        generator = extension2.on_execute()
        next(generator, None)

    def test_calculate_complexity_handles_empty_document(self, mock_execution_context) -> None:
        """Test complexity calculation handles empty document.

        Given: Empty/None document
        When: _calculate_query_complexity() is called
        Then: Returns 0
        """
        extension = QueryComplexityLimitExtension(execution_context=mock_execution_context)

        complexity = extension._calculate_query_complexity(None)
        assert complexity == 0

    def test_list_field_increases_complexity(self, mock_execution_context) -> None:
        """Test list fields increase complexity score.

        Given: Query with list field (plural name)
        When: Complexity is calculated
        Then: Complexity is higher than single field
        """
        # Single field query
        single_doc = Mock(spec=['definitions'])
        single_def = Mock(spec=['selection_set'])
        single_field = Mock(spec=['name', 'selection_set'])
        single_field.name = Mock(value="user")  # Singular (not a list)
        single_field.selection_set = None
        single_def.selection_set = Mock(spec=['selections'], selections=[single_field])
        single_doc.definitions = [single_def]

        # List field query
        list_doc = Mock(spec=['definitions'])
        list_def = Mock(spec=['selection_set'])
        list_field = Mock(spec=['name', 'selection_set'])
        list_field.name = Mock(value="users")  # Plural (list field)
        list_field.selection_set = None
        list_def.selection_set = Mock(spec=['selections'], selections=[list_field])
        list_doc.definitions = [list_def]

        extension = QueryComplexityLimitExtension(execution_context=mock_execution_context)

        single_complexity = extension._calculate_query_complexity(single_doc)
        list_complexity = extension._calculate_query_complexity(list_doc)

        # List field should have higher complexity
        assert list_complexity > single_complexity

    def test_complexity_error_message_includes_details(
        self, mock_execution_context, complex_list_query_document
    ) -> None:
        """Test error message includes complexity details.

        Given: Query exceeding complexity limit
        When: Exception is raised
        Then: Error message includes actual complexity and max complexity
        """
        mock_execution_context.graphql_document = complex_list_query_document
        extension = QueryComplexityLimitExtension(
            execution_context=mock_execution_context, max_complexity=50
        )

        with pytest.raises(Exception) as exc_info:
            generator = extension.on_execute()
            next(generator)

        error_message = str(exc_info.value)
        assert "50" in error_message  # max_complexity
        assert "complexity" in error_message.lower()


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.graphql
class TestIntrospectionControlExtension:
    """Comprehensive tests for introspection control."""

    @pytest.fixture
    def mock_execution_context(self) -> Mock:
        """Provide mock GraphQL execution context.

        Returns:
            Mock ExecutionContext
        """
        context = Mock()
        context.query = "query { __schema { types { name } } }"
        return context

    @pytest.fixture
    def introspection_schema_document(self) -> Mock:
        """Provide introspection query document (__schema).

        Returns:
            Mock document with __schema introspection
        """
        document = Mock(spec=['definitions'])
        definition = Mock(spec=['selection_set'])
        field = Mock(spec=['name', 'selection_set'])
        field.name = Mock(value="__schema")
        field.selection_set = None
        definition.selection_set = Mock(spec=['selections'], selections=[field])
        document.definitions = [definition]

        return document

    @pytest.fixture
    def introspection_type_document(self) -> Mock:
        """Provide introspection query document (__type).

        Returns:
            Mock document with __type introspection
        """
        document = Mock(spec=['definitions'])
        definition = Mock(spec=['selection_set'])
        field = Mock(spec=['name', 'selection_set'])
        field.name = Mock(value="__type")
        field.selection_set = None
        definition.selection_set = Mock(spec=['selections'], selections=[field])
        document.definitions = [definition]

        return document

    @pytest.fixture
    def regular_query_document(self) -> Mock:
        """Provide regular (non-introspection) query document.

        Returns:
            Mock document with regular query
        """
        document = Mock(spec=['definitions'])
        definition = Mock(spec=['selection_set'])
        field = Mock(spec=['name', 'selection_set'])
        field.name = Mock(value="users")
        field.selection_set = None
        definition.selection_set = Mock(spec=['selections'], selections=[field])
        document.definitions = [definition]

        return document

    @patch.object(settings, "DEBUG", True)
    def test_introspection_allowed_in_debug_mode(
        self, mock_execution_context, introspection_schema_document
    ) -> None:
        """Test introspection is allowed when DEBUG=True.

        Given: DEBUG=True, introspection query
        When: on_execute() is called
        Then: Query is allowed
        """
        mock_execution_context.graphql_document = introspection_schema_document
        extension = IntrospectionControlExtension(execution_context=mock_execution_context)

        # Should not raise exception in DEBUG mode
        generator = extension.on_execute()
        next(generator, None)

    @patch.object(settings, "DEBUG", False)
    @patch.object(settings, "GRAPHQL_ENABLE_INTROSPECTION", True)
    def test_introspection_allowed_when_explicitly_enabled(
        self, mock_execution_context, introspection_schema_document
    ) -> None:
        """Test introspection allowed when explicitly enabled.

        Given: DEBUG=False, GRAPHQL_ENABLE_INTROSPECTION=True
        When: Introspection query is made
        Then: Query is allowed
        """
        mock_execution_context.graphql_document = introspection_schema_document
        extension = IntrospectionControlExtension(execution_context=mock_execution_context)

        # Should not raise exception when explicitly enabled
        generator = extension.on_execute()
        next(generator, None)

    @patch.object(settings, "DEBUG", False)
    @patch.object(settings, "GRAPHQL_ENABLE_INTROSPECTION", False)
    def test_introspection_blocked_in_production(
        self, mock_execution_context, introspection_schema_document
    ) -> None:
        """Test introspection is blocked in production.

        Given: DEBUG=False, GRAPHQL_ENABLE_INTROSPECTION=False
        When: Introspection query (__schema) is made
        Then: Exception is raised
        """
        mock_execution_context.graphql_document = introspection_schema_document
        extension = IntrospectionControlExtension(execution_context=mock_execution_context)

        # Should raise exception in production
        with pytest.raises(Exception) as exc_info:
            generator = extension.on_execute()
            next(generator)

        assert "introspection" in str(exc_info.value).lower()
        assert "disabled" in str(exc_info.value).lower()

    @patch.object(settings, "DEBUG", False)
    @patch.object(settings, "GRAPHQL_ENABLE_INTROSPECTION", False)
    def test_type_introspection_blocked_in_production(
        self, mock_execution_context, introspection_type_document
    ) -> None:
        """Test __type introspection is blocked in production.

        Given: DEBUG=False, introspection disabled
        When: __type query is made
        Then: Exception is raised
        """
        mock_execution_context.graphql_document = introspection_type_document
        extension = IntrospectionControlExtension(execution_context=mock_execution_context)

        # Should raise exception for __type introspection
        with pytest.raises(Exception) as exc_info:
            generator = extension.on_execute()
            next(generator)

        assert "introspection" in str(exc_info.value).lower()

    @patch.object(settings, "DEBUG", False)
    @patch.object(settings, "GRAPHQL_ENABLE_INTROSPECTION", False)
    def test_regular_queries_allowed_in_production(
        self, mock_execution_context, regular_query_document
    ) -> None:
        """Test regular queries are allowed even when introspection disabled.

        Given: DEBUG=False, introspection disabled
        When: Regular query (not introspection) is made
        Then: Query is allowed
        """
        mock_execution_context.graphql_document = regular_query_document
        extension = IntrospectionControlExtension(execution_context=mock_execution_context)

        # Should not raise exception for regular queries
        generator = extension.on_execute()
        next(generator, None)

    def test_is_introspection_query_detects_schema(
        self, mock_execution_context, introspection_schema_document
    ) -> None:
        """Test _is_introspection_query detects __schema.

        Given: Query with __schema field
        When: _is_introspection_query() is called
        Then: Returns True
        """
        extension = IntrospectionControlExtension(execution_context=mock_execution_context)

        is_introspection = extension._is_introspection_query(introspection_schema_document)
        assert is_introspection is True

    def test_is_introspection_query_detects_type(
        self, mock_execution_context, introspection_type_document
    ) -> None:
        """Test _is_introspection_query detects __type.

        Given: Query with __type field
        When: _is_introspection_query() is called
        Then: Returns True
        """
        extension = IntrospectionControlExtension(execution_context=mock_execution_context)

        is_introspection = extension._is_introspection_query(introspection_type_document)
        assert is_introspection is True

    def test_is_introspection_query_regular_query(
        self, mock_execution_context, regular_query_document
    ) -> None:
        """Test _is_introspection_query returns False for regular queries.

        Given: Regular query (no __schema or __type)
        When: _is_introspection_query() is called
        Then: Returns False
        """
        extension = IntrospectionControlExtension(execution_context=mock_execution_context)

        is_introspection = extension._is_introspection_query(regular_query_document)
        assert is_introspection is False

    def test_is_introspection_query_handles_empty_document(self, mock_execution_context) -> None:
        """Test _is_introspection_query handles empty document.

        Given: Empty/None document
        When: _is_introspection_query() is called
        Then: Returns False
        """
        extension = IntrospectionControlExtension(execution_context=mock_execution_context)

        is_introspection = extension._is_introspection_query(None)
        assert is_introspection is False


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.graphql
class TestSecurityExtensionIntegration:
    """Test integration of multiple security extensions."""

    @pytest.fixture
    def mock_execution_context(self) -> Mock:
        """Provide mock GraphQL execution context.

        Returns:
            Mock ExecutionContext
        """
        context = Mock()
        context.query = "query { users { posts { comments } } }"
        return context

    def test_all_extensions_can_be_initialized_together(self, mock_execution_context) -> None:
        """Test all security extensions can be initialized together.

        Given: Execution context
        When: All three extensions are initialized
        Then: No conflicts or errors occur
        """
        depth_ext = QueryDepthLimitExtension(execution_context=mock_execution_context)
        complexity_ext = QueryComplexityLimitExtension(execution_context=mock_execution_context)
        introspection_ext = IntrospectionControlExtension(execution_context=mock_execution_context)

        assert depth_ext is not None
        assert complexity_ext is not None
        assert introspection_ext is not None

    def test_extensions_have_independent_configuration(self, mock_execution_context) -> None:
        """Test each extension maintains independent configuration.

        Given: Extensions with different settings
        When: Extensions are initialized
        Then: Each maintains its own configuration
        """
        depth_ext = QueryDepthLimitExtension(execution_context=mock_execution_context, max_depth=5)
        complexity_ext = QueryComplexityLimitExtension(
            execution_context=mock_execution_context, max_complexity=500
        )

        assert depth_ext.max_depth == 5
        assert complexity_ext.max_complexity == 500
