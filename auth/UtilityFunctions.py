import pickle


def save_auth_details(platform, auth_details):
    with open(f"{platform}_auth.pkl", 'wb') as f:
        pickle.dump(auth_details, f)


def load_auth_details(platform):
    try:
        with open(f"{platform}_auth.pkl", 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None
