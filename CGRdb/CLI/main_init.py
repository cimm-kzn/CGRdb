# -*- coding: utf-8 -*-
#
#  Copyright 2018-2021 Ramil Nugmanov <nougmanoff@protonmail.com>
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
from LazyPony import LazyEntityMeta
from pony.orm import Database, db_session


def init_core(args):
    db = Database()
    LazyEntityMeta.attach(db, database='CGRdb_config')
    db.bind('postgres', **args.connection)
    db.generate_mapping(create_tables=True)

    with db_session:
        db.execute('CREATE EXTENSION IF NOT EXISTS intarray')
        db.execute('CREATE EXTENSION IF NOT EXISTS plpython3u')
