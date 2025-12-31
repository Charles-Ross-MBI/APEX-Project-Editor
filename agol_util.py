import json
import requests
import streamlit as st
import logging


# Pull Username and Password
agol_username = st.session_state['AGOL_USERNAME']
agol_password = st.session_state['AGOL_PASSWORD']



def format_guid(value) -> str:
    if isinstance(value, list):
        if not value:
            return None
        value = value[0]

    if not value or not isinstance(value, str):
        return None

    clean_value = value.strip().lstrip("{").rstrip("}")
    parts = clean_value.split("-")
    if len(parts) != 5 or not all(parts):
        return None

    return f"{{{clean_value}}}"


def get_agol_token() -> str:
    url = "https://www.arcgis.com/sharing/rest/generateToken"

    data = {
        "username": agol_username,
        "password": agol_password,
        "referer": "https://www.arcgis.com",
        "f": "json"
    }

    try:
        response = requests.post(url, data=data)

        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

        token_data = response.json()

        if "token" in token_data:
            return token_data["token"]
        elif "error" in token_data:
            raise ValueError(f"Authentication failed: {token_data['error']['message']}")
        else:
            raise ValueError("Unexpected response format: Token not found.")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to ArcGIS Online: {e}")


def get_unique_field_values(
    url: str,
    field: str,
    where: str = "1=1",
    sort_type: str = None,
    sort_order: str = "asc"
) -> list:

    try:
        token = get_agol_token()
        if not token:
            raise ValueError("Authentication failed: Invalid token.")

        params = {
            "where": where,
            "outFields": field,
            "returnDistinctValues": "true",
            "returnGeometry": "false",
            "f": "json",
            "token": token
        }

        query_url = f"{url}/query"
        response = requests.get(query_url, params=params)

        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

        data = response.json()
        if "error" in data:
            raise Exception(f"API Error: {data['error']['message']} - {data['error'].get('details', [])}")

        available_fields = {field_info["name"] for field_info in data.get("fields", [])}
        if field not in available_fields:
            raise ValueError(f"Field '{field}' does not exist. Available fields: {available_fields}")

        unique_values = []
        for feature in data.get("features", []):
            attributes = feature.get("attributes", {})
            if field in attributes and attributes[field] not in unique_values:
                unique_values.append(attributes[field])

        if sort_type:
            reverse = sort_order.lower() == "desc"

            if sort_type.lower() == "alpha":
                unique_values.sort(key=lambda x: str(x).lower(), reverse=reverse)
            elif sort_type.lower() == "numeric":
                try:
                    unique_values.sort(key=lambda x: float(x), reverse=reverse)
                except ValueError:
                    raise ValueError("Numeric sorting failed: field contains non-numeric values.")

        return unique_values

    except requests.exceptions.RequestException as req_error:
        raise Exception(f"Network error occurred: {req_error}")
    except ValueError as val_error:
        raise ValueError(val_error)
    except Exception as gen_error:
        raise Exception(gen_error)


def get_multiple_fields(url: str, fields: list = None) -> list:
    try:
        token = get_agol_token()
        if not token:
            raise ValueError("Authentication failed: Invalid token.")

        out_fields = ",".join(fields) if fields else "*"

        params = {
            "where": "1=1",
            "outFields": out_fields,
            "returnGeometry": "false",
            "f": "json",
            "token": token
        }

        query_url = f"{url}/query"
        response = requests.get(query_url, params=params)

        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

        data = response.json()
        if "error" in data:
            raise Exception(f"API Error: {data['error']['message']} - {data['error'].get('details', [])}")

        results = []
        for feature in data.get("features", []):
            attributes = feature.get("attributes", {})
            results.append({k: v for k, v in attributes.items()})

        return results

    except Exception as e:
        raise Exception(f"Error retrieving project records: {e}")


def select_record(url: str, id_field: str, id_value: str, fields="*", return_geometry=False):
    try:
        token = get_agol_token()
        if not token:
            raise ValueError("Authentication failed: Invalid token.")

        params = {
            "where": f"{id_field}='{id_value}'",
            "outFields": fields,
            "returnGeometry": str(return_geometry).lower(),
            "outSR": 4326,
            "f": "json",
            "token": token
        }

        query_url = f"{url}/query"
        response = requests.get(query_url, params=params)

        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

        data = response.json()
        if "error" in data:
            raise Exception(f"API Error: {data['error']['message']} - {data['error'].get('details', [])}")

        return data.get("features", [])

    except Exception as e:
        raise Exception(f"Error retrieving project record: {e}")


def delete_project(url: str, globalid: str) -> bool:
    try:
        token = get_agol_token()
        if not token:
            raise ValueError("Authentication failed: Invalid token.")

        params = {
            "where": f"GlobalID='{globalid}'",
            "f": "json",
            "token": token
        }

        delete_url = f"{url}/deleteFeatures"

        response = requests.post(delete_url, data=params)
        result = response.json()

        if "deleteResults" in result:
            success = all(r.get("success", False) for r in result["deleteResults"])
            return True
        else:
            print("Unexpected response:", result)
            return False

    except Exception as e:
        print(f"Error deleting project: {e}")
        return False


class AGOLQueryIntersect:
    def __init__(self, url, geometry, fields="*", return_geometry=False,
                 list_values=None, string_values=None):

        self.url = url
        self.geometry = self._swap_coords(geometry)
        self.fields = fields
        self.return_geometry = return_geometry
        self.list_values_field = list_values
        self.string_values_field = string_values
        self.token = self._authenticate()

        self.results = self._execute_query()

        self.list_values = []
        if self.list_values_field:
            self.list_values = self._extract_unique_values(self.list_values_field)

        self.string_values = ""
        if self.string_values_field:
            unique_list = self._extract_unique_values(self.string_values_field)
            self.string_values = ",".join(map(str, unique_list))

    def _authenticate(self):
        token = get_agol_token()
        if not token:
            raise ValueError("Authentication failed: Invalid token.")
        return token

    def _swap_coords(self, geometry):
        if isinstance(geometry, list):
            if len(geometry) == 2 and all(isinstance(coord, (int, float)) for coord in geometry):
                return [geometry[1], geometry[0]]
            elif all(isinstance(coord, list) and len(coord) == 2 for coord in geometry):
                return [[pt[1], pt[0]] for pt in geometry]
        return geometry

    def _build_geometry(self):
        if isinstance(self.geometry, list):
            if len(self.geometry) == 2 and all(isinstance(coord, (int, float)) for coord in self.geometry):
                geometry_dict = {
                    "x": self.geometry[0],
                    "y": self.geometry[1],
                    "spatialReference": {"wkid": 4326}
                }
                geometry_type_str = "esriGeometryPoint"

            elif all(
                isinstance(coord, list) and len(coord) == 2 and
                all(isinstance(val, (int, float)) for val in coord)
                for coord in self.geometry
            ):
                if len(self.geometry) >= 2:
                    geometry_dict = {
                        "paths": [self.geometry],
                        "spatialReference": {"wkid": 4326}
                    }
                    geometry_type_str = "esriGeometryPolyline"
                else:
                    raise ValueError("Invalid geometry: A line must have at least two coordinate pairs.")
            else:
                raise ValueError("Invalid geometry format.")
        else:
            raise ValueError("Invalid geometry: Geometry must be a list.")

        return geometry_dict, geometry_type_str

    def _execute_query(self):
        geometry_dict, geometry_type_str = self._build_geometry()

        params = {
            "geometry": json.dumps(geometry_dict),
            "geometryType": geometry_type_str,
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "where": "1=1",
            "outFields": self.fields,
            "returnGeometry": self.return_geometry,
            "outSR": 4326,
            "f": "json",
            "token": self.token
        }

        query_url = f"{self.url}/query"
        response = requests.get(query_url, params=params)

        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

        data = response.json()
        if "error" in data:
            raise Exception(f"API Error: {data['error']['message']} - {data['error'].get('details', [])}")

        results = []
        requested_fields = [f.strip() for f in self.fields.split(",") if f.strip()]
        for feature in data.get("features", []):
            attributes = feature.get("attributes", {})
            filtered_attrs = {f: attributes.get(f) for f in requested_fields} if self.fields != "*" else attributes
            feature_package = {"attributes": filtered_attrs}
            if self.return_geometry:
                feature_package["geometry"] = feature.get("geometry", {})
            results.append(feature_package)

        return results

    def _extract_unique_values(self, field_name):
        if not self.results:
            return []
        available_fields = {f for feature in self.results for f in feature["attributes"].keys()}
        if field_name not in available_fields:
            return []
        values = [feature["attributes"].get(field_name) for feature in self.results if feature["attributes"].get(field_name) is not None]
        return list(set(values))


class AGOLDataLoader:
    def __init__(self, url: str):
        self.url = url.rstrip("/")
        self.token = self._authenticate()
        self.success = False
        self.message = None
        self.globalids = []

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("AGOLDataLoader")

    def _authenticate(self):
        token = get_agol_token()
        if not token:
            raise ValueError("Authentication failed: Invalid token.")
        return token

    def add_features(self, payload: dict):
        endpoint = f"{self.url}/applyEdits"
        self.logger.info("Starting add_features process...")

        try:
            resp = requests.post(
                endpoint,
                data={
                    "f": "json",
                    "token": self.token,
                    "adds": json.dumps(payload["adds"])
                }
            )
            self.logger.info("Raw response text: %s", resp.text)
            result = resp.json()

            if "addResults" in result:
                add_results = result["addResults"]
                failures = [r for r in add_results if not r.get("success")]

                if failures:
                    self.success = False
                    error_messages = []
                    for r in failures:
                        err = r.get("error")
                        if err:
                            error_messages.append(
                                f"Code {err.get('code')}: {err.get('description')}"
                            )
                    self.message = (
                        f"Failed to add {len(failures)} feature(s). "
                        f"Errors: {', '.join(error_messages)}"
                    )
                    self.logger.error(self.message)
                else:
                    self.success = True
                    self.message = "All features added successfully."
                    self.globalids = [
                        r.get("globalId") for r in add_results if r.get("success")
                    ]
                    self.logger.info(self.message)
            else:
                self.success = False
                self.message = f"Unexpected response: {result}"
                self.logger.error(self.message)

        except Exception as e:
            self.success = False
            self.message = f"Error during add_features: {str(e)}"
            self.logger.exception(self.message)

        return {
            "success": self.success,
            "message": self.message,
            "globalids": self.globalids
        }
    
    def update_features(self, payload: dict):
        """
        Sends an update payload to the AGOL applyEdits endpoint.
        Returns success status, message, and updated global IDs.
        """

        endpoint = f"{self.url}/applyEdits"
        self.logger.info("Starting update_features process...")

        try:
            resp = requests.post(
                endpoint,
                data={
                    "f": "json",
                    "token": self.token,
                    "updates": json.dumps([payload])  # AGOL expects a list
                }
            )

            self.logger.info("Raw response text: %s", resp.text)
            result = resp.json()

            # Ensure updateResults exists
            if "updateResults" in result:
                update_results = result["updateResults"]
                failures = [r for r in update_results if not r.get("success")]

                # Handle failures
                if failures:
                    self.success = False
                    error_messages = []

                    for r in failures:
                        err = r.get("error")
                        if err:
                            error_messages.append(
                                f"Code {err.get('code')}: {err.get('description')}"
                            )

                    self.message = (
                        f"Failed to update {len(failures)} feature(s). "
                        f"Errors: {', '.join(error_messages)}"
                    )
                    self.logger.error(self.message)

                # Handle success
                else:
                    self.success = True
                    self.message = "All features updated successfully."
                    self.globalids = [
                        r.get("globalId") for r in update_results if r.get("success")
                    ]
                    self.logger.info(self.message)

            else:
                self.success = False
                self.message = f"Unexpected response: {result}"
                self.logger.error(self.message)

        except Exception as e:
            self.success = False
            self.message = f"Error during update_features: {str(e)}"
            self.logger.exception(self.message)

        return {
            "success": self.success,
            "message": self.message,
            "globalids": self.globalids
        }

    



class AGOLRecordLoader:
    """
    Loads a single AGOL record using select_record() and stores
    all attributes + geometry into Streamlit session_state.

    Access values through:
        loader.attributes
        loader.geometry
        loader.<fieldname>  (dynamic attributes)
    """

    def __init__(self, url, id_field, id_value,
                 prefix="", fields="*", return_geometry=True):

        self.url = url
        self.id_field = id_field
        self.id_value = id_value
        self.fields = fields
        self.return_geometry = return_geometry

        # Normalize prefix
        self.prefix = prefix.rstrip("_") + "_" if prefix else ""

        # Fetch the record
        self.record = self._fetch_record()

        # Extract attributes + geometry
        self.attributes = self.record.get("attributes", {})
        self.geometry = self.record.get("geometry", None)

        # Store in session_state
        self._store_in_session_state()

        # Create dynamic attributes for direct access
        self._create_dynamic_attributes()

    # ---------------------------------------------------------
    # Fetch record from AGOL
    # ---------------------------------------------------------
    def _fetch_record(self):
        results = select_record(
            url=self.url,
            id_field=self.id_field,
            id_value=self.id_value,
            fields=self.fields,
            return_geometry=self.return_geometry
        )

        if not results:
            raise ValueError(f"No record found for {self.id_field} = {self.id_value}")

        # select_record returns a list → take the first feature
        return results[0]

    # ---------------------------------------------------------
    # Store values in Streamlit session_state
    # ---------------------------------------------------------
    def _store_in_session_state(self):
        for key, value in self.attributes.items():
            lower_key = key.lower()
            st.session_state[f"{self.prefix}{lower_key}"] = value

        # Geometry stored as lowercase too
        st.session_state[f"{self.prefix}geometry"] = self.geometry

    # ---------------------------------------------------------
    # Create dynamic attributes for direct access
    # ---------------------------------------------------------
    def _create_dynamic_attributes(self):
        for key, value in self.attributes.items():
            lower_key = key.lower()
            setattr(self, lower_key, value)

        setattr(self, "geometry", self.geometry)


