import asyncio
import aiohttp
import json

from distutils.version import LooseVersion


class Branch:
    '''
    Branch class represents binary packages for branch in Simply Linux repository
    '''

    URL_BRANCH_BINARY_PACKAGES = 'https://rdb.altlinux.org/api/export/branch_binary_packages/'
    URL_ALL_PKGSET_ARCHS = 'https://rdb.altlinux.org/api/site/all_pkgset_archs?branch='

    def __init__(self, branch: str) -> None:
        self.branch = branch
        self.comparsion_result = None
        # Event loop for async http requests
        ioloop = asyncio.get_event_loop()
        # Get all branch archetectures
        self.raw_archs = ioloop.run_until_complete(self._ask_api(self.URL_ALL_PKGSET_ARCHS))
        if 'errors' in self.raw_archs:
            raise Exception(self.raw_archs['errors'])

        # List of archetectures for future use
        self.archs_set = [i['arch'] for i in self.raw_archs['archs']]

        # Get all packages for branch arch via event loop
        self.raw_packages = ioloop.run_until_complete(self._get_packages_for_arch())

        # Fill package sets for future comparsion
        self.packages_sets = {}
        for arch in self.raw_packages:
            if 'errors' in arch:
                continue
            self.packages_sets[arch['request_args']['arch']] = {'packages_set': {i['name'] for i in arch['packages']},
                                                                'packages': {i['name']: i for i in arch['packages']}}
        ioloop.close()

    async def _ask_api(self, URL: str, params: dict = {}) -> dict:
        '''
        Send async HTTP GET request to API
        '''
        req_url = f'{URL}{self.branch}'
        if params:
            req_url = f'{req_url}?'
            for param in params.items():
                req_url = f'{req_url}{param[0]}={param[1]}&'
        async with aiohttp.ClientSession() as session:
            async with session.get(req_url) as resp:
                return json.loads(await resp.text())

    async def _get_packages_for_arch(self) -> list:
        '''
        Prepare _ask_api Futures list to run it in event loop
        '''
        arch_packages_data = []
        futures = [self._ask_api(self.URL_BRANCH_BINARY_PACKAGES, {'arch': i}) for i in self.archs_set]
        for d in asyncio.as_completed(futures):
            arch_packages_data.append(await d)

        return arch_packages_data

    @staticmethod
    def _prepare_list(r_set: set, data: list) -> list:
        '''
        Static method to create part of comparsion result structure
        '''
        lst = list(r_set)
        lst.sort()
        return [(p, data['packages'][p]['version']) for p in lst]

    def compare(self, other: 'Branch') -> None:
        '''
        Method compares current Branch oject with other one
        '''
        # Data structure for comparsion result
        self.comparsion_result = {'current_branch': self.branch, 'compared_to_branch': other.branch, 'result': {}}

        for arch, data in self.packages_sets.items():
            # Each archetecture in own dict
            self.comparsion_result['result'][arch] = {}
            # Packages added to current branch compared to other branch
            added_names = data['packages_set'] - other.packages_sets[arch]['packages_set']
            self.comparsion_result['result'][arch]['added'] = self._prepare_list(added_names, data)

            # Packages removed from current branch compared to other branch
            removed_names = other.packages_sets[arch]['packages_set'] - data['packages_set']
            self.comparsion_result['result'][arch]['removed'] = self._prepare_list(removed_names, other.packages_sets[arch])

            # Packages updated in current branch compared to other branch
            intersected = list(data['packages_set'].intersection(other.packages_sets[arch]['packages_set']))
            intersected.sort()
            updated = []
            suspicious = []
            for p in intersected:
                try:
                    if LooseVersion(data['packages'][p]['version']) > LooseVersion(other.packages_sets[arch]['packages'][p]['version']):
                        updated.append((p, data['packages'][p]['version'], other.packages_sets[arch]['packages'][p]['version']))
                except TypeError:
                    # Packages which versions impossible to compare
                    suspicious.append((p, data['packages'][p]['version'], other.packages_sets[arch]['packages'][p]['version']))
            self.comparsion_result['result'][arch]['updated'] = updated
            self.comparsion_result['result'][arch]['suspicious'] = suspicious

    def compare_results_as_json(self) -> str:
        '''
        Return comparsion results as json
        '''
        return json.dumps(self.comparsion_result)

    def __repr__(self):
        return f'Branch(\'{self.branch}\')'
