# This file is bridge for separate models where each model is defined in its own file

from app.__init__ import db

# models
from .users import User
from .files import File
from .invoices import Invoices
from .emissions import Emissions
from .services_emissions import services_emissions
