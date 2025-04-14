import json
import os
import shutil
import logging

import requests

from dotenv import load_dotenv

load_dotenv(".env")

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://graph.mapillary.com"
SAVE_IMAGES_DIR = "data/images"
SAVE_IMAGES_METADATA_DIR = "data/metadata"

def setup_dirs():
    os.makedirs(SAVE_IMAGES_DIR, exist_ok=True)
    os.makedirs(SAVE_IMAGES_METADATA_DIR, exist_ok=True)

    logger.info(f"Created directories: {SAVE_IMAGES_DIR}, {SAVE_IMAGES_METADATA_DIR}")


def download_images(image_ids=None, bbox=None, creators=None):
    """
    Download images from Mapillary given a list of image IDs or a bbox [minLon, minLat, maxLon, maxLat].
    """

    # only image_ids or bbox should be provided
    if not image_ids and not bbox:
        raise ValueError("Either image_ids or bbox must be provided.")
    if image_ids and bbox:
        raise ValueError("Only one of image_ids or bbox should be provided.")
    if image_ids:
        for image_id in image_ids:
            logger.info(f"Downloading image {image_id}")
            download_image(image_id)
    elif bbox:
        logger.info(f"Downloading images in bbox {bbox}")
        if creators:
            logger.info(f"Filtering images by creators: {creators}")
            for creator in creators:
                # Fetch image IDs from Mapillary API using bbox
                image_url = f"{BASE_URL}/images?access_token={os.getenv('MAPILLARY_API_TOKEN')}&bbox={','.join(map(str, bbox))}&creator_username={creator}&fields=thumb_original_url,computed_geometry,captured_at,computed_compass_angle,creator"
                logger.debug(f"Fetching image IDs from {image_url}")
                response = requests.get(image_url)

                if response.status_code == 200:
                    data = response.json()
                    image_ids = [image["id"] for image in data["data"]]
                    for image_id in image_ids:
                        download_image(image_id)
                else:
                    logger.info(f"Failed to fetch images in bbox {bbox}: {response.status_code}")
                    logger.debug(f"bbox fetch response: {response.json()}")

def download_image(image_id):
    """
    Download an image from Mapillary given its ID.
    """

    image_url = f"{BASE_URL}/{image_id}?access_token={os.getenv('MAPILLARY_API_TOKEN')}&fields=thumb_original_url,computed_geometry,captured_at,computed_compass_angle"
    logger.debug(f"Fetching image metadata from {image_url}")
    response = requests.get(image_url)

    if response.status_code == 200:
        data = response.json()
        logger.debug(f"JSON response: {data}")
        image_url = data["thumb_original_url"]
        metadata = {"computed_geometry": data["computed_geometry"],
                    "captured_at": data["captured_at"],
                    "computed_compass_angle": data["computed_compass_angle"]}
        
        # Download the image
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            logger.info(f"Downloading image:{image_id}")
            
            image_path = os.path.join(SAVE_IMAGES_DIR, f"{image_id}.jpg")
            with open(image_path, "wb") as f:
                f.write(image_response.content)
        
        else:
            logger.info(f"Failed to download image {image_id}: {image_response.status_code}")
            logger.debug(f"image_response: {image_response.json()}")
            return None
        
        # Save metadata
        with open(os.path.join(SAVE_IMAGES_METADATA_DIR, f"{image_id}.json"), "w") as f:
            json.dump(metadata, f)
        
        logger.info(f"Saved metadata for image {image_id}")

    else:
        logger.info(f"Failed to fetch image metadata {image_id}: {response.status_code}")
        logger.debug(f"Metadata fetch response: {response.json()}")
        return None
    
    # Save image and metadata
    logger.info(f"Saved image {image_id} to {SAVE_IMAGES_DIR}")
    logger.info(f"Saved metadata {image_id} to {SAVE_IMAGES_METADATA_DIR}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download images from Mapillary given their IDs.")
    parser.add_argument("--image_ids", nargs="+", help="List of Image IDs to download", default=None)
    parser.add_argument("--bbox", nargs=4, type=float, help="Bounding box coordinates [minLon, minLat, maxLon, maxLat]", default=None)
    parser.add_argument("--creators", nargs="+", help="List of creator usernames to filter images", default=None)
    args = parser.parse_args()

    setup_dirs()
    download_images(image_ids=args.image_ids, bbox=args.bbox, creators=args.creators)