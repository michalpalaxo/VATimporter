from os import rename, listdir, remove
from ConfigParser import SafeConfigParser
import sys
import time
import logging


# Helpers
def move_from_input_to_error_folder(fullname):
    rename(parser.get('directories', 'sourceFolder') + fullname, parser.get('directories', 'ErrorFolderPath') + fullname)


def move_from_input_to_success_folder(fullname):
    rename(parser.get('directories', 'sourceFolder') + fullname, parser.get('directories', 'SuccessFolderPath') + fullname)


def rename_and_move_from_input_to_success_folder(fullname, new_name):
    rename(parser.get('directories', 'sourceFolder') + fullname, parser.get('directories', 'SuccessFolderPath') + new_name)


# Delete everything in uploader ack folder
def empty_acknowledge(folder_path):
    try:
        files = listdir(folder_path)
        for f in files:
            remove(folder_path+'/'+f)
        return True
    except Exception, e:
        logging.error(e)
        return False


# Write test
def write_test(path):
    try:
        f = open(path+"temp.txt", 'w')
        f.write("write test")
        f.close()
        return True
    except Exception, e:
        logging.error(e)
        return False


# Read test
def read_test(path):
    try:
        f = open(path+"temp.txt", 'r')
        f.readline()
        f.close()
        return True
    except Exception, e:
        logging.error(e)
        return False


# Delete test
def delete_test(path):
    try:
        remove(path+"temp.txt")
        return True
    except Exception, e:
        logging.error(e)
        return False


# Main processing function
def process(fullname):
    try:
        name = fullname[:fullname.rfind(".")]

        data_line = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>"
        data_line = data_line + "\n<document>"
        data_line = data_line + "\n\t<definition>VAT</definition>"
        data_line = data_line + "\n\t<indexdata>"
        if name.count('_') > 5:
            logging.error('ERROR: Number of values greater than expected for ' + fullname)
            raise Exception('ERROR: Number of values greater than expected for ' + fullname)
        if name.count('_') < 5:
            logging.error('ERROR: Number of values less than expected for ' + fullname)
            raise Exception('ERROR: Number of values less than expected for ' + fullname)
        name2 = name.replace("@", "")
        values = name2.split("_")

        cif_no = values[1]
        doc_id = values[2]
        unprocessed_date = values[3]
        vat_ref_no = values[4]
        invoice_type = values[5]
        processed_date = "01/01/1900"

        if len(unprocessed_date) == 6:
            processed_date = "01/" + unprocessed_date[0:2] + "/" + unprocessed_date[2:6]

        data_line = data_line + "\n\t\t<STMNT_DATE>" + processed_date + "</STMNT_DATE>"
        data_line = data_line + "\n\t\t<CIF_NO>" + cif_no + "</CIF_NO>"
        data_line = data_line + "\n\t\t<DOC_ID>" + doc_id + "</DOC_ID>"
        data_line = data_line + "\n\t\t<VAT_REF_NO>" + vat_ref_no + "</VAT_REF_NO>"
        data_line = data_line + "\n\t\t<INVOICE_TYPE>" + invoice_type + "</INVOICE_TYPE>"
        data_line = data_line + "\n\t</indexdata>"
        data_line = data_line + "\n\t<appfile>" + fullname + "</appfile>"
        data_line = data_line + "\n</document>"
        move_from_input_to_success_folder(fullname)
        f = open(parser.get('directories', 'SuccessFolderPath') + name + '.xml', 'w')
        f.write(data_line)
        f.close()
        return

    except Exception, err:
        logging.debug(err)
        logging.debug('Failed to process. File=' + fullname)
        move_from_input_to_error_folder(fullname)


def run():
    logging.debug("Purging acknowledge Folder")
    if not empty_acknowledge(parser.get('directories', 'acknowledgeFolder')):
        logging.error("Unable to purge acknowledge folder")
    else:
        logging.debug("Acknowledge folder purged")
    dir_list = listdir(parser.get('directories', 'sourceFolder'))
    logging.info('Files Found = '+str(len(dir_list)))
    if len(dir_list) == 0:
        logging.debug('\n\t\t+++++Nothing to Process(VAT Parser V1.0)+++++++')
    else:
        for name in dir_list:
            logging.info('Processing File=' + name)
            if process(name):
                logging.debug('Successfully processed File=' + name)
    logging.debug('\n\t+++++Going to sleep for ' + parser.get('directories', 'sleepTime')+" seconds +++++++")
    time.sleep(float(parser.get('directories', 'sleepTime')))


logging.basicConfig(filename='XML-Utility.log', level=logging.DEBUG)
parser = SafeConfigParser()
parser.read('config.ini')
logging.debug('\t\t\t=====Configurations====')
logging.debug('\t\tFolder to error files = '+parser.get("directories", "ErrorFolderPath"))
logging.debug('\t\tFolder to Success files = '+parser.get('directories', 'SuccessFolderPath'))
logging.debug('\t\tSource Folder = '+parser.get('directories', 'sourceFolder'))
everythingOK = True
logging.debug('\t\t\t======Diagnostic Test VAT scan Parser V1.0=======')

if write_test(parser.get('directories', 'ErrorFolderPath')):
    logging.debug('Write test to '+parser.get('directories', 'ErrorFolderPath')+"  => Success")
else:
    everythingOK = False
    logging.debug('Write test to '+parser.get('directories', 'ErrorFolderPath')+"  => Fail")

if write_test(parser.get('directories', 'SuccessFolderPath')):
    logging.debug('Write test to '+parser.get('directories', 'SuccessFolderPath')+"  => Success")
else:
    everythingOK = False
    logging.debug('Write test to '+parser.get('directories', 'SuccessFolderPath')+"  => Fail")

if write_test(parser.get('directories', 'sourceFolder')):
    logging.debug('Write test to '+parser.get('directories', 'sourceFolder')+"  => Success")
else:
    everythingOK = False
    logging.debug('Write test to '+parser.get('directories', 'sourceFolder')+"  => Fail")

if not everythingOK:
    logging.debug('\n\t\t++++++++DIAGNOSTICS FAILED. UTILITY ABORTED+++++++')
    sys.exit(1)

if read_test(parser.get('directories', 'ErrorFolderPath')):
    logging.debug('Read test to '+parser.get('directories', 'ErrorFolderPath')+"  => Success")
else:
    everythingOK = False
    logging.debug('Read test to '+parser.get('directories', 'ErrorFolderPath')+"  => Fail")

if read_test(parser.get('directories', 'SuccessFolderPath')):
    logging.debug('Read test to '+parser.get('directories', 'SuccessFolderPath')+"  => Success")
else:
    everythingOK = False
    logging.debug('Read test to '+parser.get('directories', 'SuccessFolderPath')+"  => Fail")

if read_test(parser.get('directories', 'sourceFolder')):
    logging.debug('Read test to '+parser.get('directories', 'sourceFolder')+"  => Success")
else:
    everythingOK = False
    logging.debug('Read test to '+parser.get('directories', 'sourceFolder')+"  => Fail")

if not everythingOK:
    logging.debug('\n\t\t++++++++DIAGNOSTICS FAILED. UTILITY ABORTED+++++++')
    sys.exit(1)

if delete_test(parser.get('directories', 'ErrorFolderPath')):
    logging.debug('Delete test to '+parser.get('directories', 'ErrorFolderPath')+"  => Success")
else:
    everythingOK = False
    logging.debug('Delete test to '+parser.get('directories', 'ErrorFolderPath')+"  => Fail")

if delete_test(parser.get('directories', 'SuccessFolderPath')):
    logging.debug('Delete test to '+parser.get('directories', 'SuccessFolderPath')+"  => Success")
else:
    everythingOK = False
    logging.debug('Delete test to '+parser.get('directories', 'SuccessFolderPath')+"  => Fail")

if delete_test(parser.get('directories', 'sourceFolder')):
    logging.debug('Delete test to '+parser.get('directories', 'sourceFolder')+"  => Success")
else:
    everythingOK = False
    logging.debug('Delete test to '+parser.get('directories', 'sourceFolder')+"  => Fail")

if not everythingOK:
    logging.debug('\n\t\t++++++++DIAGNOSTICS FAILED. UTILITY ABORTED+++++++')
    sys.exit(1)

while True:
    run()
