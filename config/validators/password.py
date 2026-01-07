"""Enhanced password validators for stronger security requirements.

This module provides custom password validators that enforce security best practices
beyond Django's built-in validators. These validators check for:
- Minimum uppercase and lowercase letters
- Minimum number of digits
- Minimum number of special characters
- Password complexity scoring
- No sequential characters
- No repeated characters

Note: Django's built-in validators already handle:
- CommonPasswordValidator: Rejects passwords in common password lists
- UserAttributeSimilarityValidator: Prevents passwords similar to username/email
"""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """Validate password complexity requirements.

    This validator enforces the following requirements:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character from: !@#$%^&*()_+-=[]{}|;:,.<>?

    These requirements help ensure passwords are resistant to brute force
    and dictionary attacks.
    """

    def __init__(
        self,
        min_uppercase: int = 1,
        min_lowercase: int = 1,
        min_digits: int = 1,
        min_special: int = 1,
    ) -> None:
        """Initialize the validator with complexity requirements.

        Args:
            min_uppercase: Minimum number of uppercase letters required.
            min_lowercase: Minimum number of lowercase letters required.
            min_digits: Minimum number of digits required.
            min_special: Minimum number of special characters required.
        """
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special

    def validate(self, password: str, user=None) -> None:
        """Validate the password meets complexity requirements.

        Args:
            password: The password to validate.
            user: The user instance (optional, for context-aware validation).

        Raises:
            ValidationError: If the password does not meet complexity requirements.
        """
        errors = []

        # Check for uppercase letters
        if len(re.findall(r"[A-Z]", password)) < self.min_uppercase:
            errors.append(
                _(
                    f"Password must contain at least {self.min_uppercase} "
                    "uppercase letter(s)."
                )
            )

        # Check for lowercase letters
        if len(re.findall(r"[a-z]", password)) < self.min_lowercase:
            errors.append(
                _(
                    f"Password must contain at least {self.min_lowercase} "
                    "lowercase letter(s)."
                )
            )

        # Check for digits
        if len(re.findall(r"\d", password)) < self.min_digits:
            errors.append(
                _(f"Password must contain at least {self.min_digits} digit(s).")
            )

        # Check for special characters
        special_chars = r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]"
        if len(re.findall(special_chars, password)) < self.min_special:
            errors.append(
                _(
                    f"Password must contain at least {self.min_special} "
                    "special character(s) from: "
                    "!@#$%^&*()_+-=[]{}|;:,.<>?"
                )
            )

        if errors:
            raise ValidationError(errors)

    def get_help_text(self) -> str:
        """Return help text for password complexity requirements.

        Returns:
            A description of the password complexity requirements.
        """
        return _(
            f"Password must contain at least {self.min_uppercase} "
            f"uppercase letter(s), {self.min_lowercase} lowercase letter(s), "
            f"{self.min_digits} digit(s), and {self.min_special} special "
            f"character(s)."
        )


class MinimumLengthValidator:
    """Validate minimum and maximum password length.

    Django's default minimum length is 8 characters. This validator enforces
    a minimum of 12 characters for better security. It also enforces a maximum
    length to prevent DoS attacks from very long passwords.
    """

    def __init__(self, min_length: int = 12, max_length: int = 128) -> None:
        """Initialize the validator with length requirements.

        Args:
            min_length: Minimum number of characters required (default: 12).
            max_length: Maximum number of characters allowed (default: 128).
        """
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password: str, user=None) -> None:
        """Validate the password meets length requirements.

        Args:
            password: The password to validate.
            user: The user instance (optional, for context-aware validation).

        Raises:
            ValidationError: If the password is too short or too long.
        """
        if len(password) < self.min_length:
            raise ValidationError(
                _(f"Password must be at least {self.min_length} characters long."),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

        if len(password) > self.max_length:
            raise ValidationError(
                _(f"Password must not exceed {self.max_length} characters (maximum length)."),
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self) -> str:
        """Return help text for length requirements.

        Returns:
            A description of the length requirements.
        """
        return _(
            f"Password must be at least {self.min_length} characters long "
            f"and no more than {self.max_length} characters."
        )


class MaximumLengthValidator:
    """Validate maximum password length to prevent DoS attacks.

    Very long passwords can cause excessive CPU usage during hashing.
    This validator enforces a reasonable maximum length.
    """

    def __init__(self, max_length: int = 128) -> None:
        """Initialize the validator with maximum length requirement.

        Args:
            max_length: Maximum number of characters allowed.
        """
        self.max_length = max_length

    def validate(self, password: str, user=None) -> None:
        """Validate the password does not exceed maximum length.

        Args:
            password: The password to validate.
            user: The user instance (optional, for context-aware validation).

        Raises:
            ValidationError: If the password is too long.
        """
        if len(password) > self.max_length:
            raise ValidationError(
                _(f"Password must not exceed {self.max_length} characters."),
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self) -> str:
        """Return help text for maximum length requirement.

        Returns:
            A description of the maximum length requirement.
        """
        return _(f"Password must not exceed {self.max_length} characters.")


class NoSequentialCharactersValidator:
    """Prevent sequential characters in passwords (e.g., '12345', 'abcdef').

    Sequential characters make passwords easier to guess and should be avoided.
    This validator detects sequences of 3 or more consecutive characters.
    """

    def __init__(self, max_sequence_length: int = 3) -> None:
        """Initialize the validator with maximum sequence length.

        Args:
            max_sequence_length: Maximum allowed length of sequential characters.
        """
        self.max_sequence_length = max_sequence_length

    def validate(self, password: str, user=None) -> None:
        """Validate the password does not contain long sequential characters.

        Args:
            password: The password to validate.
            user: The user instance (optional, for context-aware validation).

        Raises:
            ValidationError: If the password contains sequential characters.
        """
        # Check for sequential numbers
        for i in range(len(password) - self.max_sequence_length + 1):
            if password[i : i + self.max_sequence_length].isdigit():
                # Check if digits are sequential
                seq = password[i : i + self.max_sequence_length]
                digits = [int(d) for d in seq]
                is_ascending = all(
                    digits[j] + 1 == digits[j + 1]
                    for j in range(len(digits) - 1)
                )
                is_descending = all(
                    digits[j] - 1 == digits[j + 1]
                    for j in range(len(digits) - 1)
                )
                if is_ascending or is_descending:
                    raise ValidationError(
                        _(
                            f"Password must not contain sequential numbers "
                            f"( {seq} )."
                        ),
                        code="sequential_numbers",
                    )

        # Check for sequential letters
        for i in range(len(password) - self.max_sequence_length + 1):
            if password[i : i + self.max_sequence_length].isalpha():
                seq = password[i : i + self.max_sequence_length]
                chars = seq.lower()
                # Check if letters are sequential
                is_ascending = all(
                    ord(chars[j]) + 1 == ord(chars[j + 1])
                    for j in range(len(chars) - 1)
                )
                is_descending = all(
                    ord(chars[j]) - 1 == ord(chars[j + 1])
                    for j in range(len(chars) - 1)
                )
                if is_ascending or is_descending:
                    raise ValidationError(
                        _(
                            f"Password must not contain sequential letters "
                            f"({seq})."
                        ),
                        code="sequential_letters",
                    )

    def get_help_text(self) -> str:
        """Return help text for sequential characters restriction.

        Returns:
            A description of the sequential characters restriction.
        """
        return _(
            f"Password must not contain {self.max_sequence_length} or more "
            "sequential characters (e.g., 123, abc)."
        )


class NoRepeatedCharactersValidator:
    """Prevent repeated characters in passwords (e.g., 'aaa', '111').

    Repeated characters make passwords easier to guess and should be avoided.
    This validator detects sequences of 3 or more repeated characters.
    """

    def __init__(self, max_repeated: int = 3) -> None:
        """Initialize the validator with maximum repeated characters.

        Args:
            max_repeated: Maximum allowed consecutive repeated characters.
        """
        self.max_repeated = max_repeated

    def validate(self, password: str, user=None) -> None:
        """Validate the password does not contain repeated characters.

        Args:
            password: The password to validate.
            user: The user instance (optional, for context-aware validation).

        Raises:
            ValidationError: If the password contains repeated characters.
        """
        # Check for repeated characters
        for i in range(len(password) - self.max_repeated + 1):
            if len(set(password[i : i + self.max_repeated])) == 1:
                seq = password[i : i + self.max_repeated]
                raise ValidationError(
                    _(
                        f"Password must not contain {self.max_repeated} or more "
                        f"repeated characters ({seq})."
                    ),
                    code="repeated_characters",
                )

    def get_help_text(self) -> str:
        """Return help text for repeated characters restriction.

        Returns:
            A description of the repeated characters restriction.
        """
        return _(
            f"Password must not contain {self.max_repeated} or more "
            "consecutive repeated characters (e.g., aaa, 111)."
        )


class HIBPPasswordValidator:
    """Validate password against Have I Been Pwned database (H5).

    This validator checks if the password has appeared in known data breaches
    using the HIBP k-anonymity API. Only the first 5 characters of the
    SHA-1 hash are sent to preserve privacy (k-anonymity model).

    Security Review Recommendation H5:
    "Implement breach checking during registration and password change operations."
    """

    def __init__(self, threshold: int = 1, timeout: int = 2) -> None:
        """Initialise HIBP validator.

        Args:
            threshold: Minimum breach count to reject password (default: 1).
            timeout: HTTP request timeout in seconds (default: 2).
        """
        self.threshold = threshold
        self.timeout = timeout

    def validate(self, password: str, user=None) -> None:
        """Validate password against HIBP database.

        Uses k-anonymity model: only first 5 chars of SHA-1 hash are sent
        to the HIBP API. Full hash comparison happens locally.

        Args:
            password: The password to validate.
            user: Optional user instance for context.

        Raises:
            ValidationError: If password found in breach database above threshold.
        """
        import hashlib

        import requests

        # Calculate SHA-1 hash of password
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        try:
            # Query HIBP API with only first 5 chars (k-anonymity)
            response = requests.get(
                f"https://api.pwnedpasswords.com/range/{prefix}",
                timeout=self.timeout,
            )

            if response.status_code == 200:
                # Parse response for matching hashes
                hashes = response.text.split("\r\n")
                for hash_count in hashes:
                    if ":" not in hash_count:
                        continue
                    hash_part, count_str = hash_count.split(":")
                    if hash_part == suffix:
                        breach_count = int(count_str)
                        if breach_count >= self.threshold:
                            raise ValidationError(
                                _(
                                    "This password has been exposed in data "
                                    f"breaches {breach_count:,} times. Please "
                                    "choose a different password."
                                ),
                                code="password_breached",
                            )

        except requests.RequestException:
            # If API is unavailable, allow password change
            # (fail open to prevent blocking legitimate users)
            pass

    def get_help_text(self) -> str:
        """Return help text describing HIBP validation.

        Returns:
            Help text string.
        """
        return _(
            "Your password cannot be one that has been exposed in "
            "data breaches."
        )


class PasswordHistoryValidator:
    """Validate password against user's password history (H11).

    This validator prevents users from reusing their recent passwords.
    By default, it checks the last 5 passwords.

    Security Review Recommendation H11:
    "Prevent password reuse by checking against the last N passwords."
    """

    def __init__(self, history_count: int = 5) -> None:
        """Initialise password history validator.

        Args:
            history_count: Number of previous passwords to check (default: 5).
        """
        self.history_count = history_count

    def validate(self, password: str, user=None) -> None:
        """Validate password against user's password history.

        Args:
            password: The password to validate.
            user: Optional user instance for context.

        Raises:
            ValidationError: If password matches a recent password in history.
        """
        if user is None:
            return

        # Import here to avoid circular imports
        from apps.core.models import PasswordHistory

        if PasswordHistory.check_password_reuse(
            user, password, self.history_count
        ):
            raise ValidationError(
                _(
                    f"This password has been recently used. "
                    f"Please choose a password you haven't used in your "
                    f"last {self.history_count} passwords."
                ),
                code="password_recently_used",
            )

    def get_help_text(self) -> str:
        """Return help text describing password history validation.

        Returns:
            Help text string.
        """
        return _(
            f"Your password cannot be one of your previous "
            f"{self.history_count} passwords."
        )
