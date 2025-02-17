# -*- coding: utf-8 -*-
#
#  Copyright 2017-2021 Ramil Nugmanov <nougmanoff@protonmail.com>
#  Copyright 2019 Adelia Fatykhova <adelik21979@gmail.com>
#  This file is part of CGRdb.
#
#  CGRdb is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
from importlib import import_module
from json import load
from LazyPony import LazyEntityMeta
from pkg_resources import get_distribution, DistributionNotFound, VersionConflict
from pony.orm import db_session, Database
from ..sql import *


def create_core(args):
    major_version = '.'.join(get_distribution('CGRdb').version.split('.')[:-1])
    schema = args.name
    config = args.config and load(args.config) or {}
    if 'packages' not in config:
        config['packages'] = []
    for p in config['packages']:
        try:
            p = get_distribution(p)
            import_module(p.project_name)
        except (DistributionNotFound, VersionConflict):
            raise ImportError(f'packages not installed or has invalid versions: {p}')

    db_config = Database()
    LazyEntityMeta.attach(db_config, database='CGRdb_config')
    db_config.bind('postgres', **args.connection)
    db_config.generate_mapping()

    with db_session:
        if db_config.Config.exists(name=schema):
            raise KeyError('schema already exists')
    with db_session:
        db_config.execute(f'DROP SCHEMA IF EXISTS {schema} CASCADE')
        db_config.execute(f'CREATE SCHEMA {schema}')

    db = Database()
    LazyEntityMeta.attach(db, schema, 'CGRdb')
    db.bind('postgres', **args.connection)
    db.generate_mapping(create_tables=True)

    with db_session:
        db.execute(f'ALTER TABLE "{schema}"."Reaction" DROP COLUMN structure')
        db.execute(f'ALTER TABLE "{schema}"."Reaction" RENAME TO "ReactionRecord"')
        db.execute(f'CREATE VIEW "{schema}"."Reaction" AS SELECT id, NULL::bytea as structure '
                   f'FROM "{schema}"."ReactionRecord"')

    with db_session:
        db.execute(init_session.replace('{schema}', schema))

        db.execute(insert_molecule.replace('{schema}', schema))
        db.execute(after_insert_molecule.replace('{schema}', schema))
        db.execute(delete_molecule.replace('{schema}', schema))
        db.execute(insert_reaction.replace('{schema}', schema))
        db.execute(merge_molecules.replace('{schema}', schema))

        db.execute(insert_molecule_trigger.replace('{schema}', schema))
        db.execute(after_insert_molecule_trigger.replace('{schema}', schema))
        db.execute(delete_molecule_trigger.replace('{schema}', schema))
        db.execute(insert_reaction_trigger.replace('{schema}', schema))

        db.execute(search_structure_molecule.replace('{schema}', schema))
        db.execute(search_structure_reaction.replace('{schema}', schema))
        db.execute(search_similar_molecules.replace('{schema}', schema))
        db.execute(search_substructure_molecule.replace('{schema}', schema))
        db.execute(search_similar_reactions.replace('{schema}', schema))
        db.execute(search_substructure_reaction.replace('{schema}', schema))
        db.execute(search_reactions_by_molecule.replace('{schema}', schema))
        db.execute(search_mappingless_reaction.replace('{schema}', schema))

    with db_session:
        db_config.Config(name=schema, config=config, version=major_version)
