
# detectors/type1/__init__.py
"""
Type 1 Clone Detection Methods
"""
from .hash_method import Type1HashMethod
from .string_method import Type1StringMethod
from .ast_exact_method import Type1ASTMethod

__all__ = ['Type1HashMethod', 'Type1StringMethod', 'Type1ASTMethod']