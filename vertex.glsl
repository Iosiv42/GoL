#version 330
layout (location=0) in vec2 aPos;

uniform mat4 proj_matrix;
uniform mat4 view_matrix;

void main() {
    gl_Position = proj_matrix * view_matrix * vec4(aPos, 0.0, 1.0);
}
