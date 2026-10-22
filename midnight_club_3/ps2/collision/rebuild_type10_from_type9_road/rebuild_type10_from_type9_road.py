#!/usr/bin/env python3
"""Reconstroi a quadtree viaria type10 com todos os pisos road do type9.

O conversor antigo alimentava o type10 somente com ``roadSG`` do BND textual.
Isso excluia ``alwaysdry*``, ``bridge*`` e toda a geometria dirigivel que veio
das instancias do .hood (asphalt, crosswalk, freeway, LAX e pontes).  Este
adaptador reutiliza o escritor/validador canonico de ``mc2_roads_to_mc3`` e
troca apenas a etapa de selecao: a fonte passa a ser o type9 ja validado e a
selecao passa a ser o material fisico global ``road`` (17).

Somente faces com |normal Y| >= 0.70 entram na rede. Faces invertidas sao
orientadas para cima, duplicatas geometricas coplanares sao removidas e a
adjacencia e reconstruida. O type9 do doador permanece byte a byte intacto.
"""

import argparse
import os
import sys
from types import SimpleNamespace


def point_key(point):
    return tuple(round(value, 5) for value in point)


def polygon_key(points):
    return tuple(sorted(point_key(point) for point in points))


def prepare_type9_roads(path, _suffixes):
    import mc3_bound as MB
    import mc2_roads_to_mc3 as roads

    source = MB.Bound(path)
    node = source.trees[9]
    source_vertices, source_polygons = source.geometry(node)
    palette = source.materials(node)
    material_indices = source.material_indices(node)
    road_global = MB.GLOBAL_MATERIAL_IDS['road']

    vertices = []
    vertex_map = {}
    polygons = []
    seen = set()
    stats = {
        'source': os.path.abspath(path),
        'source_vertices': len(source_vertices),
        'source_polygons': len(source_polygons),
        'source_road_polygons': 0,
        'selected': 0,
        'duplicate_polygons': 0,
        'degenerate_polygons': 0,
        'nonhorizontal_polygons': 0,
        'reversed_polygons': 0,
        'material_global_id': road_global,
    }

    for poly, local_material in zip(source_polygons, material_indices):
        if local_material >= len(palette) or palette[local_material] != road_global:
            continue
        stats['source_road_polygons'] += 1
        old_indices = list(poly[2])
        points = [tuple(source_vertices[index]) for index in old_indices]
        normal, area = roads.normal_e_area(points)
        if normal is None:
            stats['degenerate_polygons'] += 1
            continue
        if abs(normal[1]) < 0.70:
            stats['nonhorizontal_polygons'] += 1
            continue
        if normal[1] < 0:
            points.reverse()
            normal, area = roads.normal_e_area(points)
            stats['reversed_polygons'] += 1
        key = polygon_key(points)
        if key in seen:
            stats['duplicate_polygons'] += 1
            continue
        seen.add(key)

        indices = []
        for point in points:
            key_point = point_key(point)
            index = vertex_map.get(key_point)
            if index is None:
                index = len(vertices)
                vertex_map[key_point] = index
                vertices.append(point)
            indices.append(index)
        polygons.append((normal, area, tuple(indices), 'type9:road'))

    if not polygons:
        raise ValueError('type9 nao forneceu nenhum piso road horizontal')
    if len(vertices) > 0xFFFF or len(polygons) > 0xFFFF:
        raise ValueError('type10 excede u16: %d vertices, %d poligonos' %
                         (len(vertices), len(polygons)))

    neighbors = [[0xFFFF] * len(poly[2]) for poly in polygons]
    edges = {}
    for polygon_index, (_normal, _area, indices, _material) in enumerate(polygons):
        for edge_index, first in enumerate(indices):
            second = indices[(edge_index + 1) % len(indices)]
            edge = (min(first, second), max(first, second))
            edges.setdefault(edge, []).append((polygon_index, edge_index))

    paired = 0
    nonmanifold = 0
    for uses in edges.values():
        if len(uses) == 2 and uses[0][0] != uses[1][0]:
            (left, left_edge), (right, right_edge) = uses
            neighbors[left][left_edge] = right
            neighbors[right][right_edge] = left
            paired += 1
        elif len(uses) > 2:
            nonmanifold += 1

    stats.update(
        selected=len(polygons),
        output_vertices=len(vertices),
        output_polygons=len(polygons),
        paired_edges=paired,
        boundary_edges=sum(value == 0xFFFF for row in neighbors for value in row),
        nonmanifold_edges=nonmanifold,
        header={'source_kind': 9, 'selection': 'global material road (17)'},
    )
    return vertices, polygons, neighbors, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True,
                        help='PCK cujo type9 road alimentara o type10')
    parser.add_argument('--donor', required=True,
                        help='PCK cujo type9 sera preservado e type10 substituido')
    parser.add_argument('--tools', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--audit')
    parser.add_argument('--depth', type=int, default=8)
    parser.add_argument('--per-leaf', type=int, default=40)
    args = parser.parse_args()

    sys.path.insert(0, args.tools)
    import mc2_roads_to_mc3 as roads

    roads.prepare_roads = prepare_type9_roads
    build_args = SimpleNamespace(
        mc2=args.source,
        donor=args.donor,
        out=args.out,
        audit=args.audit,
        materials='type9-road-global-17',
        depth=args.depth,
        per_leaf=args.per_leaf,
    )
    roads.build(build_args)


if __name__ == '__main__':
    main()
