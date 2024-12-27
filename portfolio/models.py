from sqlalchemy import text
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from typing import List
from flask_login import UserMixin


from portfolio import Base

from sqlalchemy import select


