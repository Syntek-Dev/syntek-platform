# Coding Principles for Syntek Platform

This document outlines the fundamental coding principles that guide development across the Syntek CMS platform.

## Rob Pike's 5 Rules of Programming

### Rule 1: You can't tell where a program is going to spend its time
**Bottlenecks occur in surprising places, so don't try to second guess and put in a speed hack until you've proven that's where the bottleneck is.**

**Applied to Syntek Platform:**
- Profile GraphQL queries before optimizing resolvers
- Measure React render performance before adding useMemo
- Test database query performance before adding indexes
- Use Django's debug toolbar and PostgreSQL EXPLAIN ANALYZE

### Rule 2: Measure. Don't tune for speed until you've measured
**And even then don't unless one part of the code overwhelms the rest.**

**Applied to Syntek Platform:**
- Use Strawberry's query profiling for API performance
- Implement Apollo Client DevTools for frontend performance
- Monitor Rust security layer with profiling tools
- Set up Prometheus metrics for production monitoring

### Rule 3: Fancy algorithms are slow when n is small
**And n is usually small. Fancy algorithms have big constants.**

**Applied to Syntek Platform:**
- Simple Django ORM queries over complex raw SQL (until proven necessary)
- Basic React state management before Redux/Zustand
- Straightforward GraphQL resolvers before complex DataLoaders
- Simple Rust functions before advanced async patterns

### Rule 4: Fancy algorithms are buggier than simple ones
**And harder to implement. Use simple algorithms as well as simple data structures.**

**Applied to Syntek Platform:**
- Clear GraphQL schema design over clever type unions
- Simple React component hierarchies over complex HOCs
- Explicit Django model relationships over generic foreign keys
- Direct Rust security checks over elaborate middleware chains

### Rule 5: Data dominates
**If you've chosen the right data structures and organized things well, the algorithms will almost always be self-evident.**

**Applied to Syntek Platform:**
- Design PostgreSQL schema first, then build GraphQL schema around it
- Create clear React prop interfaces before implementing components
- Define Rust data structures before implementing security logic
- Structure Django models to reflect business domain clearly

## Linus Torvalds Principles

### "Good taste in programming"
**The right solution is often the most elegant and simple one.**

**Applied to Syntek Platform:**
- Prefer GraphQL field resolvers over complex REST endpoints
- Use TypeScript interfaces to enforce data contracts
- Write Rust code that compiles on first try with clear error handling
- Design React components that are self-explanatory

### "Show me your flowcharts and conceal your tables, and I shall continue to be mystified"
**Data structures are more important than algorithms.**

**Applied to Syntek Platform:**
- Focus on PostgreSQL database design as foundation
- Create clear GraphQL types that match business entities
- Design React component props interfaces first
- Structure Rust security data models before implementing functions

### "Talk is cheap. Show me the code."
**Implementation matters more than documentation or theory.**

**Applied to Syntek Platform:**
- Working GraphQL mutations over extensive API documentation
- Functional React components over detailed design mockups
- Tested Rust security code over theoretical security models
- Deployed Django features over architectural planning

## Platform-Specific Guidelines

### GraphQL Schema Design
```python
# Good: Clear, domain-focused types
@strawberry.type
class Page:
    id: strawberry.ID
    title: str
    content: str
    template: Template
    created_by: User

# Avoid: Generic, unclear types
@strawberry.type
class Entity:
    data: JSON
    metadata: JSON
```

### React Component Design
```typescript
// Good: Clear props interface
interface PageBuilderProps {
  page: Page;
  onSave: (page: Page) => void;
  isReadOnly: boolean;
}

// Avoid: Unclear prop passing
interface ComponentProps {
  data: any;
  handlers: { [key: string]: Function };
}
```

### Rust Security Code
```rust
// Good: Explicit error handling
pub fn validate_token(token: &str) -> Result<Claims, AuthError> {
    match decode_jwt(token) {
        Ok(claims) => Ok(claims),
        Err(_) => Err(AuthError::InvalidToken)
    }
}

// Avoid: Hidden error cases
pub fn validate_token(token: &str) -> Claims {
    decode_jwt(token).unwrap()
}
```

### Django Model Design
```python
# Good: Clear business domain models
class Page(models.Model):
    title = models.CharField(max_length=255)
    content = models.JSONField()
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

# Avoid: Generic data models
class ContentEntity(models.Model):
    data = models.JSONField()
    metadata = models.JSONField()
```

## Performance Guidelines

### Database (PostgreSQL)
- Use `select_related()` and `prefetch_related()` for GraphQL resolvers
- Add database indexes based on actual query patterns, not speculation
- Use PostgreSQL EXPLAIN ANALYZE to verify query performance
- Implement database connection pooling for production

### GraphQL (Strawberry)
- Use DataLoader to prevent N+1 query problems
- Implement query depth limiting to prevent abuse
- Cache frequently accessed data with Redis
- Monitor query performance with APM tools

### Frontend (React + Next.js)
- Use React.memo() only when profiling shows re-render issues
- Implement code splitting for large components
- Leverage Next.js SSR for initial page loads
- Optimize bundle size with webpack analysis

### Security (Rust)
- Profile authentication middleware for performance bottlenecks
- Use async/await appropriately for I/O-bound operations
- Implement request caching where security policies allow
- Monitor memory usage in long-running security processes

## Code Review Checklist

### All Code
- [ ] Does this solve the actual problem (not a perceived problem)?
- [ ] Is the solution as simple as possible?
- [ ] Are the data structures well-designed?
- [ ] Is the code self-documenting?

### GraphQL Changes
- [ ] Are the types clearly named and focused?
- [ ] Do resolvers handle errors appropriately?
- [ ] Are there any potential N+1 query issues?
- [ ] Is the schema backward compatible?

### Frontend Changes
- [ ] Are components focused on a single responsibility?
- [ ] Is the TypeScript typing accurate and helpful?
- [ ] Are there any unnecessary re-renders?
- [ ] Is the accessibility compliance maintained?

### Backend Changes
- [ ] Are Django models normalized appropriately?
- [ ] Do database queries use proper ORM methods?
- [ ] Is the security model enforced correctly?
- [ ] Are migrations backward compatible?

### Security Changes
- [ ] Is error handling comprehensive and secure?
- [ ] Are there any potential security vulnerabilities?
- [ ] Is the performance impact acceptable?
- [ ] Are security policies enforced consistently?

## Testing Philosophy

### "Test behavior, not implementation"
- Test GraphQL API responses, not resolver implementation details
- Test React component output, not internal state management
- Test security policy enforcement, not middleware internals
- Test Django model behavior, not ORM query generation

### "Write tests that help you refactor"
- GraphQL schema changes should not break existing tests
- React component refactoring should pass existing behavior tests
- Security layer changes should not affect security policy tests
- Database migrations should not break existing business logic tests

## Documentation Standards

### Code Documentation
- GraphQL schema fields should have clear descriptions
- React component props should have JSDoc comments
- Rust public functions should have doc comments
- Django model fields should have help_text

### README Files
- Include setup instructions that actually work
- Provide examples of common use cases
- Explain architectural decisions briefly
- Keep documentation current with code changes

---

**Remember: The goal is not perfect code, but code that solves real problems simply and reliably.**