#!/usr/bin/env python3
"""Check what locations are loaded by area."""

from utils.location_path_finder import LocationGraph

g = LocationGraph()
g.load_module_data()

areas = {}
for loc_id, info in g.nodes.items():
    area = info.get('area_id', 'unknown')
    areas.setdefault(area, []).append(loc_id)

print('Locations by area:')
for area, locs in sorted(areas.items()):
    print(f'{area}: {sorted(locs)}')