from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette_context.middleware import ContextMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from config.main import local_configs
from core.context import (
    RequestIdPlugin,
    RequestProcessInfoPlugin,
    RequestStartTimestampPlugin,
)

roster = [
    # >>>>> Middleware Func
    (
        ContextMiddleware,
        {
            "plugins": [
                RequestIdPlugin(),
                RequestStartTimestampPlugin(),
                RequestProcessInfoPlugin(),
            ]
        },
    ),
    (GZipMiddleware, {"minimum_size": 1000}),
    # >>>>> Middleware Class
    (
        CORSMiddleware,
        {
            "allow_origins": local_configs.server.cors.allow_origins,
            "allow_credentials": local_configs.server.cors.allow_credentials,
            "allow_methods": local_configs.server.cors.allow_methods,
            "allow_headers": local_configs.server.cors.allow_headers,
            "expose_headers": local_configs.server.cors.expose_headers,
        },
    ),
    (
        TrustedHostMiddleware,
        {
            "allowed_hosts": local_configs.server.allow_hosts,
        },
    ),
]
