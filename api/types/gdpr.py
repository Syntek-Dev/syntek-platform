"""GraphQL types for GDPR compliance operations.

This module defines Strawberry GraphQL types for GDPR-related data
including data export requests, account deletion requests, consent
records, and processing restriction status.
"""

from datetime import datetime
from enum import Enum

import strawberry


@strawberry.enum
class ExportFormat(Enum):
    """Export file format options."""

    JSON = "json"
    CSV = "csv"


@strawberry.enum
class ExportStatus(Enum):
    """Data export request status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@strawberry.enum
class DeletionStatus(Enum):
    """Account deletion request status."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@strawberry.enum
class ConsentType(Enum):
    """Consent type categories."""

    ESSENTIAL = "essential"
    FUNCTIONAL = "functional"
    ANALYTICS = "analytics"
    MARKETING = "marketing"


@strawberry.type
class DataExportRequestType:
    """GraphQL type for data export requests.

    Represents a user's request to export their personal data
    under GDPR Article 15 (Right of Access).
    """

    id: strawberry.ID
    status: ExportStatus
    format: ExportFormat
    download_url: str | None
    expires_at: datetime | None
    created_at: datetime
    completed_at: datetime | None
    file_size: int | None
    record_counts: strawberry.scalars.JSON | None

    @staticmethod
    def from_model(export_request) -> DataExportRequestType:
        """Convert DataExportRequest model to GraphQL type.

        Args:
            export_request: DataExportRequest model instance.

        Returns:
            DataExportRequestType instance.
        """
        metadata = export_request.metadata or {}

        return DataExportRequestType(
            id=strawberry.ID(str(export_request.id)),
            status=ExportStatus(export_request.status),
            format=ExportFormat(export_request.format),
            download_url=export_request.download_url or None,
            expires_at=export_request.expires_at,
            created_at=export_request.created_at,
            completed_at=export_request.completed_at,
            file_size=metadata.get("file_size"),
            record_counts=metadata.get("record_counts"),
        )


@strawberry.type
class AccountDeletionRequestType:
    """GraphQL type for account deletion requests.

    Represents a user's request to delete their account
    under GDPR Article 17 (Right to Erasure).
    """

    id: strawberry.ID
    status: DeletionStatus
    reason: str | None
    data_retained: list[str]
    created_at: datetime
    confirmed_at: datetime | None
    completed_at: datetime | None

    @staticmethod
    def from_model(deletion_request) -> AccountDeletionRequestType:
        """Convert AccountDeletionRequest model to GraphQL type.

        Args:
            deletion_request: AccountDeletionRequest model instance.

        Returns:
            AccountDeletionRequestType instance.
        """
        return AccountDeletionRequestType(
            id=strawberry.ID(str(deletion_request.id)),
            status=DeletionStatus(deletion_request.status),
            reason=deletion_request.reason or None,
            data_retained=deletion_request.data_retained or [],
            created_at=deletion_request.created_at,
            confirmed_at=deletion_request.confirmed_at,
            completed_at=deletion_request.completed_at,
        )


@strawberry.type
class ConsentRecordType:
    """GraphQL type for consent records.

    Represents a user's consent for a specific type of data processing.
    """

    id: strawberry.ID
    consent_type: ConsentType
    granted: bool
    version: str
    granted_at: datetime
    withdrawn_at: datetime | None

    @staticmethod
    def from_model(consent) -> ConsentRecordType:
        """Convert ConsentRecord model to GraphQL type.

        Args:
            consent: ConsentRecord model instance.

        Returns:
            ConsentRecordType instance.
        """
        return ConsentRecordType(
            id=strawberry.ID(str(consent.id)),
            consent_type=ConsentType(consent.consent_type),
            granted=consent.granted,
            version=consent.version,
            granted_at=consent.granted_at,
            withdrawn_at=consent.withdrawn_at,
        )


@strawberry.type
class ProcessingRestrictionType:
    """GraphQL type for processing restriction status.

    Represents the current processing restriction status for a user
    under GDPR Article 18 (Right to Restriction of Processing).
    """

    processing_restricted: bool
    restriction_reason: str | None
    restricted_at: datetime | None
    allowed_processing: list[str] | None
    restricted_processing: list[str] | None


@strawberry.type
class DataExportPayload:
    """Response payload for data export mutation."""

    success: bool
    message: str
    export_request: DataExportRequestType | None


@strawberry.type
class AccountDeletionPayload:
    """Response payload for account deletion mutation."""

    success: bool
    message: str
    deletion_request: AccountDeletionRequestType | None


@strawberry.type
class ProcessingRestrictionPayload:
    """Response payload for processing restriction mutation."""

    success: bool
    message: str
    restriction: ProcessingRestrictionType | None


@strawberry.type
class ConsentPayload:
    """Response payload for consent mutation."""

    success: bool
    message: str
    consent: ConsentRecordType | None


@strawberry.input
class RequestDataExportInput:
    """Input for requesting a data export."""

    format: ExportFormat = ExportFormat.JSON


@strawberry.input
class RequestAccountDeletionInput:
    """Input for requesting account deletion."""

    reason: str | None = None


@strawberry.input
class ConfirmAccountDeletionInput:
    """Input for confirming account deletion."""

    token: str
    password: str


@strawberry.input
class CancelAccountDeletionInput:
    """Input for cancelling account deletion."""

    request_id: strawberry.ID


@strawberry.input
class ProcessingRestrictionInput:
    """Input for toggling processing restriction."""

    restrict: bool
    reason: str | None = None


@strawberry.input
class UpdateConsentInput:
    """Input for updating consent."""

    consent_type: ConsentType
    granted: bool
