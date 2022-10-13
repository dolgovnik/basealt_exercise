import asyncio
import aiohttp
import json


class Branch:

    URL_BRANCH_BINARY_PACKAGES = 'https://rdb.altlinux.org/api/export/branch_binary_packages/'
    URL_ALL_PKGSET_ARCHS = 'https://rdb.altlinux.org/api/site/all_pkgset_archs?branch='

    def __init__(self, branch: str):
        self.branch = branch
        ioloop = asyncio.get_event_loop()
        # Get all branch archs
        self.archs = ioloop.run_until_complete(self.ask_api(self.URL_ALL_PKGSET_ARCHS))
        if 'errors' in self.archs:
            raise Exception(self.archs['errors'])

        # Get all packages for branch arch
        self.arch_packages_data = ioloop.run_until_complete(self.get_packages_for_arch())

        # ioloop.close()

    async def ask_api(self, URL: str, params: dict = {}):
        req_url = f'{URL}{self.branch}'
        if params:
            req_url = f'{req_url}?'
            for param in params.items():
                req_url = f'{req_url}{param[0]}={param[1]}&'
        async with aiohttp.ClientSession() as session:
            async with session.get(req_url) as resp:
                return json.loads(await resp.text())

    async def get_packages_for_arch(self):
        arch_packages_data = []
        futures = [self.ask_api(self.URL_BRANCH_BINARY_PACKAGES, {'arch': i['arch']}) for i in self.archs['archs']]
        for d in asyncio.as_completed(futures):
            arch_packages_data.append(await d)

        return arch_packages_data
