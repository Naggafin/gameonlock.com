from wagtail.core import hooks


@hooks.register("register_rich_text_features")
def register_color_text_feature(features):
	feature_name = "color"
	type = "COLOR"
	tag = "span"
	description = "Color"
