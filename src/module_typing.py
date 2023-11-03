""" Module level typing (type aliases). """

from OpenGL.GL import GLuint

Pos = tuple[int, int]
GameState = set[Pos]
ShaderProgram = GLuint
Hz = float
