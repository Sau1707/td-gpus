import json
import pandas as pd
from .api import Api


def pprint(data: dict) -> None:
    """Pretty print the data"""
    print(json.dumps(data, indent=4))


class Data(Api):
    def __init__(self, api_key: str, api_token: str) -> None:
        super().__init__(api_key=api_key, api_token=api_token)

    @staticmethod
    def _load_nodes(id, data: dict) -> dict:
        """Load the nodes"""
        return {
            "id": id,
            "city": data["location"]["city"],
            "country": data["location"]["country"],
            "region": data["location"]["region"],
            "port_count": len(data["networking"]["ports"]),
            "internet_receive": data["networking"]["receive"],
            "internet_send": data["networking"]["send"],
            "cpu_amount": data["specs"]["cpu"]["amount"],
            "cpu_price": data["specs"]["cpu"]["price"],
            "cpu_type": data["specs"]["cpu"]["type"],
            "gpu_name": list(data["specs"]["gpu"].keys()),
            "ram_amount": data["specs"]["ram"]["amount"],
            "ram_price": data["specs"]["ram"]["price"],
            "storage_amount": data["specs"]["storage"]["amount"],
            "storage_price": data["specs"]["storage"]["price"],
            "listed": data["status"]["listed"],
            "online": data["status"]["online"],
            "report": data["status"]["report"],
            "reserved": data["status"]["reserved"],
            "uptime": data["status"]["uptime"]
        }

    def get_marketplace(self) -> pd.DataFrame:
        """Return the data of the user"""
        data = super().get_marketplace()
        nodes = data["hostnodes"]
        nodes = [self._load_nodes(node, nodes[node]) for node in nodes]
        df =  pd.DataFrame(nodes)
        df.set_index("id", inplace=True)
        return df
    
    def get_revenue(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return the revenue of the user"""
        data = super().get_revenue()
        df_machines = pd.DataFrame(data["result"]["data"])
        df_machines.set_index("hostnode_id", inplace=True)

        # Remove the virtual machines
        machines = df_machines.pop("virtual_machines")
        virtuals = []
        for id, machine in machines.items():
            for virtual in machine:
                virtuals.append({"hostnode_id": id, **virtual})

        df_virtuals = pd.DataFrame(virtuals)
        df_virtuals.set_index("virtual_machine_id", inplace=True)

        return df_machines, df_virtuals
    
    def get_node(self, hostnode_uuid: str) -> pd.DataFrame:
        """Return the information of a specific node"""
        raise NotImplementedError
        # data = self.get_node(hostnode_uuid)
        # return pd.DataFrame(data["data"])
    
    def get_summary(self, start: pd.Timestamp, end: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return the summary of the user"""

        # Generate the list of months in the format of 'YYYY-MM'
        date_range = pd.date_range(start=start, end=end)
        months = date_range.strftime("%Y-%m").unique()

        _df_storage = []
        _df_usage = []
        # Loop over the last 5 months
        for month in months:
            data = super().get_summary(month)
            year = int(data["bill_period"]["startY"])
            set_year = lambda x: x.replace(year=year)
            df_storage = pd.DataFrame(data["transactions"]["storage_payouts"])
            df_storage["billing_period_end"] = pd.to_datetime(df_storage['billing_period_end'], format='%m/%d').apply(set_year)
            df_storage["billing_period_start"] = pd.to_datetime(df_storage['billing_period_start'], format='%m/%d').apply(set_year)
            df_storage["type"] = "storage"

            df_usage = pd.DataFrame(data["transactions"]["vm_payouts"])
            df_usage["billing_period_end"] = pd.to_datetime(df_usage['billing_period_end'], format='%m/%d').apply(set_year)
            df_usage["billing_period_start"] = pd.to_datetime(df_usage['billing_period_start'], format='%m/%d').apply(set_year)
            df_usage["type"] = "usage"

            def expand_row(row):
                date_range = pd.date_range(start=row['billing_period_start'], end=row['billing_period_end'])
                return pd.DataFrame({
                    'date': date_range,
                    'type': row['type'],
                    'total_amount': row['total_amount'] / len(date_range), # Assuming 'amount' is distributed equally across the days
                    'hostnode_id': row['hostnode_id']
                })

            # Expand the rows, so we have one row per day
            df_storage = pd.concat([expand_row(row) for _, row in df_storage.iterrows()], ignore_index=True)
            df_usage = pd.concat([expand_row(row) for _, row in df_usage.iterrows()], ignore_index=True)

            df_storage = df_storage.groupby(['date', 'hostnode_id']).agg({'total_amount': 'sum'}).reset_index()
            df_usage = df_usage.groupby(['date', 'hostnode_id']).agg({'total_amount': 'sum'}).reset_index()
            
            df_storage.set_index("date", inplace=True)
            df_usage.set_index("date", inplace=True)

            _df_storage.append(df_storage)
            _df_usage.append(df_usage)

        df_tot_storage = pd.concat(_df_storage)
        df_tot_usage = pd.concat(_df_usage)

        return df_tot_storage, df_tot_usage