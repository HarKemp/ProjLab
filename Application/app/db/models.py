# This file is bridge for separate models where each model is defined in its own file

from app.__init__ import db

# models
from .users import User
from .files import File
from .invoices import Invoice
from .services import Service
from .emissions import Emission
from .invoices_services import invoices_services
