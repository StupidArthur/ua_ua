"""NamespaceArray configuration.

The real SUPCON server uses

    ApplicationUri    = "http://SUPCON.UAServer.Application"
    NamespaceArray[1] = "http://SUPCON.UAServer.Product"

The two are deliberately different.  asyncua's `set_application_uri()`
unconditionally writes the URI to `NamespaceArray[1]`, so the only safe
sequence is:

    1.  await server.set_application_uri(actual_app_uri)
    2.  configure product_uri / server_name / ServerArray
    3.  overwrite NamespaceArray[1] by writing the full list verbatim
    4.  assert the readback matches

After this point `set_application_uri()` and `register_namespace()` MUST
NOT be called again — they would clobber the carefully aligned
NamespaceArray.
"""

from __future__ import annotations

import logging
from typing import Iterable

from asyncua import ua


log = logging.getLogger("ua_rebuild.namespace_fix")


EXPECTED_NAMESPACE_URIS: list[str] = [
    "http://opcfoundation.org/UA/",
    "http://SUPCON.UAServer.Product",
    "http://supcon.com/UA",
    "http://opcfoundation.org/UA/Dictionary/IRDI",
    "http://opcfoundation.org/UA/DI/",
    "http://opcfoundation.org/UA/PADIM/",
    "http://www.OPCFoundation.org/UA/2013/01/ISA95",
]


async def apply_namespace_array(server, application_uri: str,
                                product_uri: str,
                                server_name: str,
                                expected_uris: list[str] | None = None) -> list[str]:
    """Apply the real server's NamespaceArray in place.

    Returns the readback list so callers can assert or log it.
    """
    if expected_uris is None:
        expected_uris = list(EXPECTED_NAMESPACE_URIS)

    # Step 1: set the ApplicationUri.  asyncua will write it into
    # NamespaceArray[1] at this point — we overwrite it immediately
    # afterwards.
    await server.set_application_uri(application_uri)

    # Step 2: product URI / server name
    server.product_uri = product_uri
    server.set_server_name(server_name)

    # Step 3: ServerArray must contain the ApplicationUri (UAExpert uses
    # it to identify the server in the project tree).
    sa_node = server.get_node(ua.NodeId(ua.ObjectIds.Server_ServerArray))
    await sa_node.write_value([application_uri])

    # Step 4: write the entire NamespaceArray verbatim.  This MUST come
    # after `set_application_uri()` so that the array is fully under our
    # control.
    ns_node = server.get_node(ua.NodeId(ua.ObjectIds.Server_NamespaceArray))
    await ns_node.write_value(expected_uris)

    # Step 5: read back and log the result.
    actual = list(await ns_node.read_value())
    log.info("[NAMESPACE] target=%s", expected_uris)
    log.info("[NAMESPACE] actual=%s", actual)

    matches = actual == expected_uris
    log.info("[NAMESPACE] exact match: %s", matches)
    if not matches:
        for i, (a, e) in enumerate(zip(actual, expected_uris)):
            if a != e:
                log.error("[NAMESPACE] mismatch at index %d: got %s expected %s",
                          i, a, e)
    return actual