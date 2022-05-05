from API.bmminer import BMMinerAPI
from miners import BaseMiner
import logging


class BMMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BMMinerAPI(ip)
        super().__init__(ip, api)
        self.model = None
        self.config = None
        self.uname = "root"
        self.pwd = "admin"

    def __repr__(self) -> str:
        return f"BMMiner: {str(self.ip)}"

    async def get_model(self) -> str or None:
        """Get miner model.

        :return: Miner model or None.
        """
        # check if model is cached
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model

        # get devdetails data
        version_data = await self.api.devdetails()

        # if we get data back, parse it for model
        if version_data:
            # handle Antminer BMMiner as a base
            self.model = version_data["DEVDETAILS"][0]["Model"].replace("Antminer ", "")
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model

        # if we don't get devdetails, log a failed attempt
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_hostname(self) -> str:
        """Get miner hostname.

        :return: The hostname of the miner as a string or "?"
        """
        if self.hostname:
            return self.hostname
        try:
            # open an ssh connection
            async with (await self._get_ssh_connection()) as conn:
                # if we get the connection, check hostname
                if conn is not None:
                    # get output of the hostname file
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    host = data.stdout.strip()

                    # return hostname data
                    logging.debug(f"Found hostname for {self.ip}: {host}")
                    self.hostname = host
                    return self.hostname
                else:
                    # return ? if we fail to get hostname with no ssh connection
                    logging.warning(f"Failed to get hostname for miner: {self}")
                    return "?"
        except Exception as e:
            # return ? if we fail to get hostname with an exception
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def send_ssh_command(self, cmd: str) -> str or None:
        """Send a command to the miner over ssh.

        :param cmd: The command to run.

        :return: Result of the command or None.
        """
        result = None

        # open an ssh connection
        async with (await self._get_ssh_connection()) as conn:
            # 3 retries
            for i in range(3):
                try:
                    # run the command and get the result
                    result = await conn.run(cmd)
                except Exception as e:
                    # if the command fails, log it
                    logging.warning(f"{self} command {cmd} error: {e}")

                    # on the 3rd retry, return None
                    if i == 3:
                        return
                    continue
        # return the result, either command output or None
        return result

    async def get_config(self) -> list or None:
        """Get the pool configuration of the miner.

        :return: Pool config data or None.
        """
        # get pool data
        pools = await self.api.pools()
        pool_data = []

        # ensure we got pool data
        if not pools:
            return

        # parse all the pools
        for pool in pools["POOLS"]:
            pool_data.append({"url": pool["URL"], "user": pool["User"], "pwd": "123"})
        return pool_data

    async def reboot(self) -> None:
        logging.debug(f"{self}: Sending reboot command.")
        await self.send_ssh_command("reboot")
        logging.debug(f"{self}: Reboot command completed.")

    async def get_data(self):
        data = {
            "IP": str(self.ip),
            "Model": "Unknown",
            "Hostname": "Unknown",
            "Hashrate": 0,
            "Temperature": 0,
            "Pool User": "Unknown",
            "Wattage": 0,
            "Split": 0,
            "Pool 1": "Unknown",
            "Pool 1 User": "Unknown",
            "Pool 2": "",
            "Pool 2 User": "",
        }
        data = await self.api.multicommand(
            "summary", "devs", "temps", "tunerstatus", "pools", "stats"
        )
        print(data)
