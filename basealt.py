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
        self.row_archs = ioloop.run_until_complete(self._ask_api(self.URL_ALL_PKGSET_ARCHS))
        if 'errors' in self.row_archs:
            raise Exception(self.row_archs['errors'])

        self.archs_set = {i['arch'] for i in self.row_archs['archs']}

        # Get all packages for branch arch
        self.raw_packages = ioloop.run_until_complete(self._get_packages_for_arch())

        # Fill package sets
        self.packages_sets = {}
        for arch in self.raw_packages:
            if 'errors' in arch:
                continue
            self.packages_sets[arch['request_args']['arch']] = {'packages_set': {i['name'] for i in arch['packages']},
                                                                'packages': {i['name']: i for i in arch['packages']}}
        # ioloop.close()

    async def _ask_api(self, URL: str, params: dict = {}):
        req_url = f'{URL}{self.branch}'
        if params:
            req_url = f'{req_url}?'
            for param in params.items():
                req_url = f'{req_url}{param[0]}={param[1]}&'
        async with aiohttp.ClientSession() as session:
            async with session.get(req_url) as resp:
                return json.loads(await resp.text())

    async def _get_packages_for_arch(self):
        arch_packages_data = []
        futures = [self._ask_api(self.URL_BRANCH_BINARY_PACKAGES, {'arch': i}) for i in self.archs_set]
        for d in asyncio.as_completed(futures):
            arch_packages_data.append(await d)

        return arch_packages_data

    def __repr__(self):
        return f'Branch(\'{self.branch}\')'
