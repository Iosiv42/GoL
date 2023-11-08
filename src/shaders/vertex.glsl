#version 330
layout (location=0) in vec2 aPos;
layout (location=1) in vec2 aOffset;

uniform mat4 proj_matrix;
uniform mat4 view_matrix;

void main() {
    gl_Position = proj_matrix * view_matrix * vec4(aPos + aOffset, 0.0, 1.0);
}
