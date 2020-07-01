import torch
from transformers import *
import torch.nn as nn
import torch.nn.functional as F
class Sbert(nn.Module):
    def __init__(self):
        super(Sbert, self).__init__()
        self.bert= BertModel.from_pretrained('bert-base-uncased')
        self.lossF=nn.MSELoss()
    def forward(self, in1,in1m,in2,in2m,label,pooling='avg'):
        loss1, a = self.bert(in1, 
                             token_type_ids=None, 
                             attention_mask=in1m)
        loss2, b = self.bert(in2, 
                             token_type_ids=None, 
                             attention_mask=in2m)
#################pooling###########################
#average#
        if pooling=='avg':
            input_mask_expanded1 = in1m.unsqueeze(-1).expand(loss1.size()).float()
            sum_embeddings1 = torch.sum(loss1 * input_mask_expanded1, 1)
            sum_mask1 = torch.clamp(input_mask_expanded1.sum(1), min=1e-9)
            output_vector1 = sum_embeddings1 / sum_mask1

            input_mask_expanded2 = in2m.unsqueeze(-1).expand(loss2.size()).float()
            sum_embeddings2 = torch.sum(loss2 * input_mask_expanded2, 1)
            sum_mask2 = torch.clamp(input_mask_expanded2.sum(1), min=1e-9)
            output_vector2 = sum_embeddings2 / sum_mask2
        
        #[cls]token#
        if pooling=='cls':
            output_vector1=loss1[:, 0, :].float() 
            output_vector2=loss2[:, 0, :].float() 
        #max#
        if pooling=='max':
            input_mask_expanded1 = in1m.unsqueeze(-1).expand(loss1.size()).float()
            loss1[input_mask_expanded1 == 0] = -1e9 
            output_vector1 = torch.max(loss1, 1)[0]

            input_mask_expanded2 = in2m.unsqueeze(-1).expand(loss2.size()).float()
            loss2[input_mask_expanded2 == 0] = -1e9 
            output_vector2 = torch.max(loss2, 1)[0]
#########cosine sim######################
        output=torch.cosine_similarity(output_vector1,output_vector2)
        output=self.lossF(output,label)
        return output