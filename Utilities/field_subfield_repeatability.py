#
#    Retrieve and scrape information from the Library of Congress MARC documentation
#    at https://www.loc.gov/marc/bibliographic/bdsummary.html (and child pages).
#
#    Write a file where each line gives a field tag, whether the field is repeatable,
#    and for each subfield code, whether it is repeatable.  For example:
#
#        018 NR $a NR $6 NR $8 R
#
#    means that field 018 is not repeatable, and can have subfields $a, $6 an $8, of
#    which only $8 is repeatable.
#
#    Usage:  python field_subfield_repeatability.py -o <output file>
#
#    The program also writes progress to the terminal and writes a log file,
#    field_subfield_repeatability.log
#
#    If you find yourself wishing for a different format, or some other change,
#    please let me know.
#
#    Version:  0.1.0  2/24/26
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#


import requests
import re
import time
import argparse
from urllib.parse import urljoin
import logging


# Create the logger
logger = logging.getLogger("SmartLogger")
logger.setLevel(logging.DEBUG)  # Allow all messages to enter the pipeline

# File Handler: Captures everything (DEBUG and up)
file_handler = logging.FileHandler("field_subfield_repeatability.log")
file_handler.setLevel(logging.DEBUG)

# Console Handler: Captures only important stuff (INFO and up)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a format for both
formatter = logging.Formatter('%(levelname)s: %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_concise_links(base_url, session):
    logger.info(f"Requesting base URL: {base_url}")
    try:
        response = session.get(base_url, timeout=10)
        logger.debug(f"Received response: {response.status_code}")
        response.raise_for_status()
        current_page = response.text
        
        logger.debug("Searching for 'Concise' links using regex...")
        pattern = r'"(.*?)">Concise</a>'
        links = re.findall(pattern, current_page)
        
        urls = [urljoin(base_url, link) for link in links]
        logger.debug(f"Found {len(urls)} links.")
        return urls
    except Exception as e:
        logger.error(f"Error finding links: {e}")
        return []


def process_child_pages(urls, out_f, session, delay=5):
    for i, url in enumerate(urls):
        if i > 0:
            logger.debug(f"Waiting {delay} seconds...")
            time.sleep(delay)
        
        logger.info(f"Fetching {url}...")
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            current_page = response.text
            logger.debug(f"Successfully retrieved {len(current_page)} bytes.")
            
            # Extract and print specific parts of <h1>: 3 digits at start and (R) or (NR) at end
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', current_page, re.IGNORECASE | re.DOTALL)
            if h1_match:
                h1_raw = h1_match.group(1).strip()
                h1_clean = re.sub(r'<[^>]+>', '', h1_raw) # Remove nested tags
                
                # Look for 3 digits at start and (R) or (NR) at end
                refined_match = re.search(r'^(\d{3}).*\(((?:R|NR))\)\s*$', h1_clean, re.IGNORECASE | re.DOTALL)
                if refined_match:
                    tag = refined_match.group(1)
                    display_text = f"{tag} {refined_match.group(2)}"
                    logger.info(f"Found H1: {display_text}")
                else:
                    logger.error(f"H1 found but format didn't match: {h1_clean}")
                    continue
            else:
                logger.error("No H1 tag found.")
                continue

            # 00X fields don't have subfields, so skip them
            if tag.startswith("00"):
                print(display_text, file=out_f)
                logger.info(display_text)
                continue

            # The page for the 880 field is anomalous, special case it
            if tag == "880":
                display_text = "880 R $6 NR"
                print(display_text, file=out_f)
                logger.info(display_text)
                continue

            subfields_found = False

            # First attempt at extracting subfields from body of the page
            subfield_pattern = r'"subfieldvalue">([^ ]+).*?\(([^)]+)\)'
            subfield_matches = re.findall(subfield_pattern, current_page, re.IGNORECASE | re.DOTALL)
            for match in subfield_matches:
                subfields_found = True
                display_text += f" {match[0]} {match[1]}"

            if subfields_found:
                logger.debug(f"Found subfields: {subfield_matches}")
                print(display_text, file=out_f)
                logger.info(display_text)
                continue

            # Second attempt at extracting subfields from the body of the page
            subfield_pattern = r'<dt>(\$[^ ]+).+?<span> \((R|NR)\)</span>'
            subfield_matches = re.findall(subfield_pattern, current_page, re.IGNORECASE | re.DOTALL)
            for match in subfield_matches:
                subfields_found = True
                display_text += f" {match[0]} {match[1]}"

            if subfields_found:
                logger.debug(f"Found subfields: {subfield_matches}")
                print(display_text, file=out_f)
                logger.info(display_text)
            else:
                logger.error(f"No subfields found for {tag} at {url}")

        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch MARC documentation and extract H1 headers.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output file for extracted tags.")
    args = parser.parse_args()

    logger.debug("Started ...")

    base_url = "https://www.loc.gov/marc/bibliographic/bdsummary.html"
    logger.info(f"Targeting base summary at: {base_url}")
    
    with requests.Session() as session:
        custom_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        session.headers.update({
            "User-Agent": custom_user_agent,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": base_url
        })

        concise_urls = get_concise_links(base_url, session)
        
        if concise_urls:
            with open(args.output, "w", encoding="utf-8") as out_f:
                process_child_pages(concise_urls, out_f, session)
            logger.info("\nAll retrievals complete.")
        else:
            logger.error("No links found to fetch.")
