from typing import Tuple
from .protobuf import *
from .util import is_third_party_panoid

def split_ietf(tag: str) -> Tuple[str, str]:
    """
    Splits an IETF language tag into its language part and country part.
    """
    parts = tag.split("-")
    lang = parts[0]
    country = parts[1] if len(parts) > 1 else parts[0]
    return lang, country

def build_find_panorama_request_url(lat, lon, radius, download_depth, locale, search_third_party, xdc):
    radius = float(radius)
    toggles = []
    include_resolution_info = True
    include_street_name_and_date = True
    include_copyright_information = True
    include_neighbors_and_historical = True
    ietf_lang, ietf_country = split_ietf(locale)

    if search_third_party:
        image_type = 10
    else:
        image_type = 2

    if download_depth:
        depth1 = {1: ProtobufEnum(0)}
        depth2 = {1: ProtobufEnum(2)}
    else:
        depth1 = {}
        depth2 = {}

    if include_resolution_info:
        toggles.append(ProtobufEnum(1))
    if include_street_name_and_date:
        toggles.append(ProtobufEnum(2))
    if include_copyright_information:
        toggles.append(ProtobufEnum(3))
    toggles.append(ProtobufEnum(4))
    if include_neighbors_and_historical:
        toggles.append(ProtobufEnum(6))
    toggles.append(ProtobufEnum(8))

    search_message = {
        1: {
            1: 'apiv3',
            5: 'US',
            11: {1: {1: False}}
        },
        2: {1: {3: lat, 4: lon}, 2: radius},
        3: {
            2: {1: ietf_lang, 2: ietf_country},
            9: {1: ProtobufEnum(2)},
            11: {
                1: {1: ProtobufEnum(image_type), 2: True, 3: ProtobufEnum(2)}
            },
        },
        4: {
            1: toggles,
            5: depth1,
            6: depth2,
        }
    }

    url = "https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=" \
            + to_protobuf_url(search_message) + f'&callback={xdc}'
            
    return url


def build_find_panorama_by_id_request_url(panoid, download_depth, locale):
    pano_type = 10 if is_third_party_panoid(panoid) else 2
    toggles = []
    include_resolution_info = True
    include_street_name_and_date = True
    include_copyright_information = True
    include_neighbors_and_historical = True
    include_places = True
    ietf_lang, ietf_country = split_ietf(locale)

    if include_resolution_info:
        toggles.append(ProtobufEnum(1))
    if include_street_name_and_date:
        toggles.append(ProtobufEnum(2))
    if include_copyright_information:
        toggles.append(ProtobufEnum(3))
    toggles.append(ProtobufEnum(4))  # does nothing?
    if include_places:
        toggles.append(ProtobufEnum(5))
    if include_neighbors_and_historical:
        toggles.append(ProtobufEnum(6))

    # these change stuff, but idk what exactly:
    toggles.append(ProtobufEnum(8))
    # toggles.append(ProtobufEnum(11))
    toggles.append(ProtobufEnum(12))
    # toggles.append(ProtobufEnum(13))

    if download_depth:
        depth1 = [{1: ProtobufEnum(1)}, {1: ProtobufEnum(2)}]
        depth2 = [{1: ProtobufEnum(1)}, {1: ProtobufEnum(2)}]
    else:
        depth1 = [{}]
        depth2 = [{}]

    # this is the protobuf message in the request URL written out as a dict
    pano_request_message = {
        1: {1: 'maps_sv.tactile', 11: {2: {1: True}}},
        2: {1: ietf_lang, 2: ietf_country},
        3: {1: {1: ProtobufEnum(pano_type), 2: panoid}},
        4: {
            1: toggles,
            2: {1: ProtobufEnum(1)},  # changing this to any other value causes huge changes;
            # haven't looked into it any further though
            4: {1: 48},  # all this does is change the size param in an icon URL
            5: depth1,
            6: depth2,
            9: {  # none of these seem to do anything
                1: [
                    {1: ProtobufEnum(2), 2: True, 3: ProtobufEnum(2)},
                    {1: ProtobufEnum(2), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(3), 2: True, 3: ProtobufEnum(2)},
                    {1: ProtobufEnum(3), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(8), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(1), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(4), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(10), 2: True, 3: ProtobufEnum(2)},
                    {1: ProtobufEnum(10), 2: False, 3: ProtobufEnum(3)}
                ]
            }
        }
    }
    url = f"https://www.google.com/maps/photometa/v1?authuser=0&hl={ietf_lang}&gl={ietf_country}&pb=" \
            + to_protobuf_url(pano_request_message)

    return url
