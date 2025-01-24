
import torch.nn as nn
from .layers import build_basic_block
from .base_color import *

# REVIEW(Rudy) - are the additional layers being added at the right place
class ModifiedColorizer(BaseColor):
    def __init__(self, config):
        super(ModifiedColorizer, self).__init__()

        dropoutLayers = config.dropoutLayers
        numExtraConv2DLayers = config.numExtraConv2DLayers
        channelMultiplier = config.channelMultiplier

        channels1 = [1, 64 * channelMultiplier, 64 * channelMultiplier]
        channels2 = [64 * channelMultiplier, 128 * channelMultiplier, 128 * channelMultiplier]
        channels3 = [128 * channelMultiplier, 256 * channelMultiplier, 256 * channelMultiplier, 256 * channelMultiplier]
        channels4 = [256 * channelMultiplier, 512 * channelMultiplier, 512 * channelMultiplier, 512 * channelMultiplier]
        channels5 = [512 * channelMultiplier, 512 * channelMultiplier, 512 * channelMultiplier, 512 * channelMultiplier]
        channels6 = [512 * channelMultiplier, 512 * channelMultiplier, 512 * channelMultiplier, 512 * channelMultiplier]
        channels7 = [512 * channelMultiplier, 512 * channelMultiplier, 512 * channelMultiplier, 512 * channelMultiplier]

        self.model1 = build_basic_block(channels=channels1, kernel_size=3, stride=[1, 2], dropout=dropoutLayers[0])
        self.model2 = build_basic_block(channels=channels2, kernel_size=3, stride=[1, 2], dropout=dropoutLayers[1])
        self.model3 = build_basic_block(channels=channels3, kernel_size=3, stride=[1, 1, 2], dropout=dropoutLayers[2])
        self.model4 = build_basic_block(channels=channels4, kernel_size=3, dropout=dropoutLayers[3])
        self.model5 = build_basic_block(channels=channels5, kernel_size=3, dilation=2, padding=2, dropout=dropoutLayers[4])
        self.model6 = build_basic_block(channels=channels6, kernel_size=3, dilation=2, padding=2, dropout=dropoutLayers[5])
        self.model7 = build_basic_block(channels=channels7, kernel_size=3, dropout=dropoutLayers[6])

        additional = []
        for _ in range(numExtraConv2DLayers):
              newLayer = build_basic_block(channels=[512 * channelMultiplier] * 4, kernel_size=3)
              additional.append(newLayer)

        self.additional_layers = nn.ModuleList(additional)

        self.model8 = build_basic_block(
              channels=[512 * channelMultiplier, 256 * channelMultiplier, 256 * channelMultiplier, 256 * channelMultiplier], kernel_size=[4, 3, 3], stride=[2, 1, 1], 
              norm_layer=False, conv_type=[nn.ConvTranspose2d, nn.Conv2d, nn.Conv2d],
              dropout=dropoutLayers[7]
        )
        self.model9 = build_basic_block(
              channels=[256 * channelMultiplier, 128 * channelMultiplier, 128 * channelMultiplier, 128 * channelMultiplier], kernel_size=[4, 3, 3], stride=[2, 1, 1], 
              norm_layer=False, conv_type=[nn.ConvTranspose2d, nn.Conv2d, nn.Conv2d],
              dropout=dropoutLayers[8]
        )
        self.model10 = build_basic_block(
              channels=[128 * channelMultiplier, 64 * channelMultiplier, 64 * channelMultiplier, 64 * channelMultiplier], kernel_size=[4, 3, 3], stride=[2, 1, 1], 
              norm_layer=False, conv_type=[nn.ConvTranspose2d, nn.Conv2d, nn.Conv2d],
              dropout=dropoutLayers[9]
        )
        self.model10.append(nn.Conv2d(64 * channelMultiplier, 313, kernel_size=1, stride=1, padding=0, bias=True))
        self.softmax = nn.Softmax(dim=1)

    def forward(self, input_l):
        conv1_2 = self.model1(self.normalize_l(input_l))
        conv2_2 = self.model2(conv1_2)
        conv3_3 = self.model3(conv2_2)
        conv4_3 = self.model4(conv3_3)
        conv5_3 = self.model5(conv4_3)
        conv6_3 = self.model6(conv5_3)
        conv7_3 = self.model7(conv6_3)

        # apply additional layers
        for layer in self.additional_layers:
            conv7_3 = layer(conv7_3)

        conv8_3 = self.model8(conv7_3)
        conv9_3 = self.model9(conv8_3)
        conv10_3 = self.model10(conv9_3)
        out_reg = self.softmax(conv10_3)
        return out_reg

def modified_colorizer(config):
	model = ModifiedColorizer(config)
	return model