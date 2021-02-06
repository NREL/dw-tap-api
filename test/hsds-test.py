import h5pyd
import json

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def connected_hsds_file(config):
    domain = config["hsds"]["domain"]
    endpoint = config["hsds"]["endpoint"]
    username = config["hsds"]["username"]
    password = config["hsds"]["password"]
    api_key = config["hsds"]["api_key"]
    try:
        # f = h5pyd.File(domain=domain,
        #                endpoint=endpoint,
        #                username=username,
        #                password=password,
        #                api_key=api_key,
        #                mode='r')

        # Debugging showed that new HSDS instance doesn't need user & pass & key
        # (in fact, they lead to errors if provided)
        f = h5pyd.File(domain=domain,
                       endpoint=endpoint,
                       mode='r')
        return f
    except OSError:
        raise InvalidUsage("Failed to access HSDS resource", status_code=403)

def available_datasets(f):
    """ Return list of all datasets available in resource f.
    """
    try:
        datasets = sorted(list(f))
    except ValueError:
        raise InvalidUsage("Problem with processing WTK datasets.")
    return datasets

with open('config.json', 'r') as f:
    config = json.load(f)

hsds_f = connected_hsds_file(config)

print("\nPrinting list of availble datasets:")
print(available_datasets(hsds_f))

print("\nPrinting small sample of windspeed data (3 values, first one should be: 10.68148):")
dset = hsds_f["windspeed_60m"]
print(dset[420:420+3, 42, 42])
