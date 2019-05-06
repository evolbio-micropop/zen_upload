#! /usr/bin/env python2.7

import argparse
import requests
import json
import os, sys
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

def main(args):

    infiles = args.infiles
    logging.info("Preparing to upload %s to zenodo.org.", infiles)

    # Read access token.
    axs_file = os.path.join(os.environ["HOME"], 'zenodo.axs')
    try:
        with open(axs_file, 'r') as fp:
            axs = fp.readline()[:-1]
        logging.debug(axs)
    except:
        raise IOError("Access token not found. Make sure your zenodo access token is saved in %s. If you don't have an access token, get one from https://zenodo.org/account/settings/applications/tokens/new/ and save it in %s" % (axs_file, axs_file))

    # Setup zenodo url and token parameters.
    zen_url = 'https://zenodo.org/api/deposit/depositions'
    params = {'access_token' : axs}

    # Test zenodo API.
    r = requests.get(zen_url, params=params)
    if not r.status_code == 200:
        logging.error("json: %s", r.json())
        raise IOError('Could not reach the zenodo api. Please check your internet connectivity and the validity of your zenodo access token.')
    else:
        logging.info('Successfully connected to the zenodo API.')
    r.close()

    # Create empty dataset.
    headers = {"Content-Type": "application/json"}
    r = requests.post(zen_url,
                      params=params,
                      headers=headers,
                      json={},
                     )
    if not r.status_code == 201:
        logging.error("json: %s", r.json())
        raise IOError('Could not create empty dataset on zenodo. Please check your internet connectivity and the validity of your zenodo access token.')
    else:
        logging.info('Successfully created empty dataset.')
        logging.debug("json: %s", r.json())
        deposit_id = r.json()['id']
        draft_url = r.json()['links']['latest_draft_html']
    r.close()

    # Add files.
    for infile in infiles:
        data = {'filename' : os.path.basename(infile)}
        logging.debug('data: %s', data)

        try:
            with open(infile, 'rb') as fp:
                files = {'file' : fp}
                r = requests.post(zen_url + "/%s/files" % deposit_id,
                                  params=params,
                                  data=data,
                                  files=files
                                  )

                if not r.status_code == 201:
                    logging.error("json: %s", r.json())
                    raise IOError('\n\tCould not add file to dataset on zenodo. Please check your internet connectivity and the validity of your zenodo access token.')

                else:
                    logging.info("Successfully uploaded %s to zenodo.", infile)
                    logging.info("Zenodo file ID: %s", r.json()['id'])
            r.close()

        except:

            # Remove unsuccessful dataset.
            logging.error("Dataset creation was not successful. Please cleanup the draft by clicking the 'Delete' button on %s." % draft_url)

            raise
            sys.exit()


    logging.info("Open %s in your browser to add metadata and publish this dataset.", draft_url)

    # Print url where to finalize the dataset.

if __name__ == "__main__":

    # Entry point
    # Setup the command line parser.
    parser = argparse.ArgumentParser()

    # Seed parameter.
    parser.add_argument("infiles",
                        nargs='+',
                        help="The file(s) to be uploaded",
                        )

    # Parse the arguments.
    args = parser.parse_args()

    main(args)

