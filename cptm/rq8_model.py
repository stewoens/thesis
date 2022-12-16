#!/usr/bin/env python3
# Copyright (c) 2019 OpenAI, HugginFace Inc. team. and TaeHwan Jung
# Copyright (c) Facebook, Inc. and its affiliates.
# ----------------------------------------------------------------------------
# MIT LICENSE
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------
"""
    Transformer model is adapted from: https://github.com/graykode/gpt-2-Pytorch
        (Commit: 46ae886391a94c6683be438269252c4afd5ba762)
    Original Paper and repository here: https://github.com/openai/gpt-2

    RNN implementation is adapted from: https://github.com/pytorch/examples/tree/master/word_language_model
"""

import copy
import math

import torch
import torch.nn as nn
from torch.nn.modules.loss import CrossEntropyLoss


def gelu(x):
    return (
        0.5
        * x
        * (1 + torch.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * torch.pow(x, 3))))
    )


class PathLSTM(nn.Module):
    def __init__(self, vocab_size, n_embd):
        super(PathLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, n_embd)
        self.LSTM = nn.LSTM(n_embd, n_embd, batch_first=True)

    def forward(self, paths):
        embed = self.embedding(paths)  # bs, max_len, max_path_len, n_embd
        batch_size, bag_size, path_len, n_embd = embed.shape
        _, (h_n, _) = self.LSTM(embed.view(batch_size * bag_size, path_len, n_embd))
        return h_n.permute((1, 0, 2)).view((batch_size, bag_size, -1))


class LayerNorm(nn.Module):
    def __init__(self, hidden_size, std_eps=1e-6):
        """Construct a layernorm module in the TF style.
        """
        super(LayerNorm, self).__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.bias = nn.Parameter(torch.zeros(hidden_size))
        self.std_eps = std_eps

    def forward(self, x):
        u = x.mean(-1, keepdim=True)
        s = (x - u).std(-1, keepdim=True)
        x = (x - u) / (s + self.std_eps)
        return self.weight * x + self.bias


class Attention(nn.Module):
    def __init__(
        self, nx, n_ctx, n_head, scale=False
    ):
        super(Attention, self).__init__()
        n_state = nx
        # [switch nx => n_state from Block to Attention to keep identical to TF implem]
        assert n_state % n_head == 0
        self.register_buffer(
            "bias", torch.tril(torch.ones(n_ctx, n_ctx)).view(1, 1, n_ctx, n_ctx)
        )
        self.n_head = n_head
        self.split_size = n_state
        self.scale = scale
        self.c_attn = nn.Linear(nx, n_state * 3)
        self.c_proj = nn.Linear(nx, n_state)

    def _attn(self, q, k, v):
        w = torch.matmul(q, k)
        if self.scale:
            w = w / math.sqrt(v.size(-1))
        nd, ns = w.size(-2), w.size(-1)
        b = self.bias[:, :, ns - nd : ns, :ns]
        w = w * b - 1e10 * (1 - b)

        w = nn.Softmax(dim=-1)(w)
        return torch.matmul(w, v)

    def merge_heads(self, x):
        x = x.permute(0, 2, 1, 3).contiguous()
        new_x_shape = x.size()[:-2] + (x.size(-2) * x.size(-1),)
        return x.view(*new_x_shape)  # in Tensorflow implem: fct merge_states

    def split_heads(self, x, k=False):
        new_x_shape = x.size()[:-1] + (self.n_head, x.size(-1) // self.n_head)
        x = x.view(*new_x_shape)  # in Tensorflow implem: fct split_states
        if k:
            return x.permute(0, 2, 3, 1)  # (batch, head, head_features, seq_length)
        else:
            return x.permute(0, 2, 1, 3)  # (batch, head, seq_length, head_features)

    def forward(self, x, layer_past=None):
        x = self.c_attn(x)
        query, key, value = x.split(self.split_size, dim=2)
        query = self.split_heads(query)
        key = self.split_heads(key, k=True)
        value = self.split_heads(value)
        if layer_past is not None:
            past_key, past_value = layer_past[0].transpose(-2, -1), layer_past[1]  # transpose back cf below
            key = torch.cat((past_key, key), dim=-1)
            value = torch.cat((past_value, value), dim=-2)
        present = torch.stack((key.transpose(-2, -1), value))
        # self attention component
        a = self._attn(query, key, value)
        a = self.merge_heads(a)
        a = self.c_proj(a)
        return a, present


class MLP(nn.Module):
    def __init__(self, n_state, n_embd):
        super(MLP, self).__init__()
        self.c_fc = nn.Linear(n_embd, n_state)
        self.c_proj = nn.Linear(n_state, n_embd)
        self.act = gelu

    def forward(self, x):
        h = self.act(self.c_fc(x))
        h2 = self.c_proj(h)
        return h2


class Block(nn.Module):
    def __init__(
        self,
        n_ctx,
        n_head,
        n_embd,
        layer_norm_epsilon,
        scale=False,
    ):
        super(Block, self).__init__()
        self.ln_1 = LayerNorm(n_embd, std_eps=layer_norm_epsilon)
        self.attn = Attention(
            n_embd, n_ctx, n_head, scale
        )
        self.ln_2 = LayerNorm(n_embd, std_eps=layer_norm_epsilon)
        self.mlp = MLP(4 * n_embd, n_embd)

    def forward(self, x, layer_past=None):
        a, present = self.attn(self.ln_1(x), layer_past=layer_past)
        x = x + a
        m = self.mlp(self.ln_2(x))
        x = x + m
        return x, present


class GPT2Model(nn.Module):
    def __init__(
        self,
        vocab_size,
        n_layer,
        n_embd,
        n_ctx,
        n_head,
        layer_norm_epsilon,
        root_paths,
    ):
        super(GPT2Model, self).__init__()
        self.n_layer = n_layer
        self.n_embd = n_embd
        self.n_vocab = vocab_size
        self.wte = nn.Embedding(vocab_size, n_embd)
        self.wpe = nn.Embedding(n_ctx, n_embd)
        if root_paths:
            self.path_lstm = PathLSTM(vocab_size, n_embd)
        block = Block(
            n_ctx,
            n_head,
            n_embd,
            layer_norm_epsilon,
            scale=True,
        )
        self.h = nn.ModuleList([copy.deepcopy(block) for _ in range(n_layer)])
        self.ln_f = LayerNorm(n_embd, std_eps=layer_norm_epsilon)

    def forward(self, input_ids, position_ids=None, paths=None, past=None):
        if past is None:
            past_length = 0
            past = [None] * len(self.h)
        else:
            past_length = past[0][0].size(-2)
        if position_ids is None:
            position_ids = torch.arange(past_length, input_ids.size(-1) + past_length, dtype=torch.long,
                                        device=input_ids.device)
            position_ids = position_ids.unsqueeze(0).expand_as(input_ids)

        input_shape = input_ids.size()
        input_ids = input_ids.view(-1, input_ids.size(-1))
        position_ids = position_ids.view(-1, position_ids.size(-1))

        inputs_embeds = self.wte(input_ids)
        position_embeds = self.wpe(position_ids)
        path_embeds = self.path_lstm(paths) if paths is not None else 0
        hidden_states = inputs_embeds + position_embeds + path_embeds
        presents = []
        for block, layer_past in zip(self.h, past):
            hidden_states, present = block(hidden_states, layer_past)
            presents.append(present)
        hidden_states = self.ln_f(hidden_states)
        output_shape = input_shape + (hidden_states.size(-1),)
        return hidden_states.view(*output_shape), presents


class GPT2LMHead(nn.Module):
    def __init__(self, model_embeddings_weights, n_embd):
        super(GPT2LMHead, self).__init__()
        self.n_embd = n_embd
        self.set_embeddings_weights(model_embeddings_weights)

    def set_embeddings_weights(self, model_embeddings_weights):
        embed_shape = model_embeddings_weights.shape
        self.decoder = nn.Linear(embed_shape[1], embed_shape[0], bias=False)
        self.decoder.weight = model_embeddings_weights  # Tied weights

    def forward(self, hidden_state):
        lm_logits = self.decoder(hidden_state)
        return lm_logits


class TransformerModel(nn.Module):
    def __init__(
        self,
        vocab_size,
        loss_fn,
        n_layer,
        n_embd,
        n_ctx,
        n_head,
        layer_norm_epsilon,
        root_paths=False,
    ):
        super(TransformerModel, self).__init__()
        self.transformer = GPT2Model(
            vocab_size,
            n_layer,
            n_embd,
            n_ctx,
            n_head,
            layer_norm_epsilon,
            root_paths,
        )
        self.lm_head = GPT2LMHead(self.transformer.wte.weight, n_embd)
        self.loss_fn = loss_fn

    def reset_parameters(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def forward(
        self, x, y, ext=None, paths=None, return_loss=False, position_ids=None, past=None
    ):
        hidden_states, presents = self.transformer(x, paths=paths, position_ids=position_ids, past=past)
        y_pred = self.lm_head(hidden_states)
        if not return_loss:
            return y_pred, presents

        # ext contains a list of idx of where to take the loss from
        # we linearize it first
        ids = []
        max_len = y.size(-1) # Max matrix width in batch
        for i, ext_i in enumerate(ext): # Iterate through all exts
            # Following line will append range from ext to max_len
            # If ext = 0 --> Append entire line
            # If ext = X --> Append from X to end of line
            ids += [i * max_len + j for j in range(ext_i, max_len)]
        # Only apply loss function on previously collected ids
        loss = self.loss_fn(y_pred.view(-1, y_pred.size(-1))[ids], y.view(-1)[ids])
        return loss

def from_file(file_path, vocab_size, pad_token, embedding_size = 300, n_layers = 6):
    model = TransformerModel(
        vocab_size,
        CrossEntropyLoss(ignore_index=-1),
        n_layers,
        embedding_size,
        1000,
        6,
        1e-5
    )
    model.load_state_dict(torch.load(file_path))
    return model