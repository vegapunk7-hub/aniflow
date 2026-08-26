"""TLS/SSL configuration for secure connections."""

from __future__ import annotations

import ssl


def create_ssl_context() -> ssl.SSLContext:
    """Create hardened SSL context for TLS 1.2+.

    Returns:
        Configured SSL context
    """
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    # Prefer forward-secrecy ciphers
    context.set_ciphers(
        "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!eNULL:!EXPORT:!DSS:!DES:!RC4:!3DES:!MD5:!PSK"
    )

    return context
