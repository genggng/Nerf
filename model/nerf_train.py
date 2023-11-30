"""
    用于创建网络、运行网络
"""
import torch
from model.nerf_model import Nerf

# 创建网络的整个流程
def create_nerf(args):
     #初始化mlp
    """
    output:
         grad_vars, #模型的梯度变量
         nerf_trained_args #字典,返回模型与mlp函数
    """
    fre_position_L      = args.fre_position_L #对位置坐标的映射维度
    fre_view_L          = args.fre_view_L #对视角的映射维度
    network_depth       = args.network_depth #8
    hidden_unit_num     = args.hidden_unit_num #256
    output_features_dim = args.output_features_dim #256
    output_dim          = args.output_dim #128
 
    mlp_model = Nerf(fre_position_L,fre_view_L,network_depth,hidden_unit_num,output_features_dim,output_dim)

    #模型的梯度变量
    grad_vars = list(mlp_model.parameters())

    #作用：运行网络生成给定点的颜色和密度
    mlp_query_fn = lambda position_inputs,view_inputs,mlp_network_fn: run_nerf(position_inputs,view_inputs,
                                                                               mlp_network_fn,
                                                                               netchunkNum = args.netchunkNum )
     
    #需要的返回值
    nerf_trained_args = { 
        'mlp_query_fn' : mlp_query_fn,
        'mlp_network_fn':mlp_model 
    }

    return grad_vars,nerf_trained_args


"""
    以批处理的形式输入到网络模型中得到输出(RGB,A)
    input:
        position_inputs:(x,y,z)position输入: tensor
        view_inputs: view输入:tensor
        mlp_network_fn: 网络model
        netchunkNum: 并行处理的输入数量:1024*64
    output:[rgb, density]

"""
def run_nerf(position_inputs,view_inputs,mlp_network_fn,netchunkNum=1024*64 ):
    

    outputs = torch.cat([mlp_network_fn(position_inputs[i:i+netchunkNum],view_inputs[i:i+netchunkNum]) 
                        for i in range(0, position_inputs.shape[0], netchunkNum)], -1)

    return outputs