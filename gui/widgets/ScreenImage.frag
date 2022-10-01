#version 440
layout(location=0) in vec2 qt_TexCoord0;
layout(location=0) out vec4 result_colour;
layout(std140, binding=0) uniform buf {
	mat4 qt_Matrix; //Required by the default vertex shader.
	float qt_Opacity; //Required by the default vertex shader.

	vec4 colour; //The colour to render the image in.
} ubuf;
layout(binding=1) uniform sampler2D image;

void main() {
	vec4 image_colour = texture(image, qt_TexCoord0);
	float brightness = (image_colour.r + image_colour.g + image_colour.b) / 3;
	result_colour = vec4(ubuf.colour.rgb * brightness, brightness);
}