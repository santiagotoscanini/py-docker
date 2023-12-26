import json
import tarfile

from app.http_client import GetRequest, make_http_request

# Possible values come from $GOOS and $GOARCH https://go.dev/doc/install/source#environment
EXPECTED_OS = "linux"
EXPECTED_ARCH = "arm"


# Registry, the open source implementation for storing and distributing container images and other content, has been
# donated to the CNCF. Registry now goes under the name of Distribution.

# The Docker Hub registry implementation is based on Distribution. Docker Hub implements version 1.0.1 OCI distribution.

def _get_registry_token(image_name: str):
    # https://distribution.github.io/distribution/spec/auth/token/
    get_token_request = GetRequest(
        base_url="https://auth.docker.io/token",
        url_params={
            "service": "registry.docker.io",
            "scope": f"repository:library/{image_name}:pull",
        },
        headers={}
    )
    response = make_http_request(get_token_request)
    token = json.loads(response.body)["token"]

    return token


def _get_image_manifest(registry_token: str, image_name: str, image_tag: str):
    # https://docs.docker.com/engine/reference/commandline/manifest
    # https://distribution.github.io/distribution/spec/api/#pulling-an-image-manifest
    # https://github.com/opencontainers/image-spec/blob/main/manifest.md

    get_manifest_request = GetRequest(
        base_url=f"https://registry.hub.docker.com/v2/library/{image_name}/manifests/{image_tag}",
        url_params={},
        headers={
            "Authorization": f"Bearer {registry_token}",

            # We can use the following header to get the manifest in Docker V2 schema 2 format.
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        }
    )
    response = make_http_request(get_manifest_request)
    manifest = json.loads(response.body.decode())

    # This is the image index, aka "fat manifest". We use it to filter manifests by os and arch.
    # https://github.com/opencontainers/image-spec/blob/main/image-index.md
    # "While the use of an image index is OPTIONAL for image providers,
    # image consumers SHOULD be prepared to process them."
    if manifest["mediaType"] == "application/vnd.oci.image.index.v1+json":
        correct_manifest = [manifest for manifest in manifest["manifests"] if
                            manifest["platform"]["os"] == EXPECTED_OS and
                            manifest["platform"]["architecture"] == EXPECTED_ARCH][0]
        download_layer_request = GetRequest(
            base_url=f"https://registry.hub.docker.com/v2/library/{image_name}/manifests/{correct_manifest['digest']}",
            url_params={},
            headers={
                "Authorization": f"Bearer {registry_token}",
                "Accept": correct_manifest["mediaType"],
            }
        )

        response = make_http_request(download_layer_request)
        manifest = json.loads(response.body.decode())

    return manifest


def _download_image_layer(registry_token: str, image_name: str, layer_digest: str, dest_dir: str):
    # https://distribution.github.io/distribution/spec/api/#pulling-a-layer
    download_layer_request = GetRequest(
        base_url=f"https://registry.hub.docker.com/v2/library/{image_name}/blobs/{layer_digest}",
        url_params={},
        headers={
            "Authorization": f"Bearer {registry_token}",
        }
    )

    response = make_http_request(download_layer_request)
    tar_file = response.body

    # This will extract the layer inside the dest_dir. So it will have the image state (directories and files).
    with open("response.tgz", "wb") as f:
        f.write(tar_file)
    tarfile.open("response.tgz").extractall(dest_dir)


def pull_image(image_name: str, image_tag: str, dest_dir: str):
    registry_token = _get_registry_token(image_name)
    manifest = _get_image_manifest(registry_token, image_name, image_tag)

    for layer in manifest["layers"]:
        _download_image_layer(registry_token, image_name, layer["digest"], dest_dir)
