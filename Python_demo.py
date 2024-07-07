# Databricks notebook source
# MAGIC %md 
# MAGIC ### DEMO: Cluster + PreInstalled PyTorch Libs 
# MAGIC
# MAGIC <!-- (init script : to establish symbolic link between 
# MAGIC  `{mounted_path_to}/.ipython/profile_pyenv/startup` & `/root/.ipython/profile_default/startup` directories such that the associated `ipython-profile-startup.py` script(s) within will append `PYTHON_LIB_PATH_MOUNTED` with pre-installed python libraries to `sys.path()` 
# MAGIC  ) -->
# MAGIC
# MAGIC <!-- 
# MAGIC Cluster: `mmt_13.3LTSML_gpu_(fasterlibloads_py)`
# MAGIC
# MAGIC Volumes init: `/Volumes/mmt_external/dais24/ext_vols/init_scripts/ipython_profile_symlink2mnt_init.sh` 
# MAGIC -->
# MAGIC

# COMMAND ----------

# DBTITLE 1,Check system paths
import sys
sys.path

# COMMAND ----------

# DBTITLE 1,Q: loaded library path?
import os
import torch_geometric

path = os.path.abspath(torch_geometric.__file__)
print('path:', path)

print('torch_geometric_version; ', torch_geometric.__version__)

# COMMAND ----------

# DBTITLE 1,Test loading torch_geometric libraries
from torch_geometric.data import Data, InMemoryDataset, DataLoader
from torch_geometric.nn import NNConv, BatchNorm, EdgePooling, TopKPooling, global_add_pool
from torch_geometric.utils import get_laplacian, to_dense_adj

# COMMAND ----------

# DBTITLE 1,Test loading torch libraries
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Sequential, Linear, ReLU, Sigmoid, Tanh, Dropout, LeakyReLU
from torch.autograd import Variable
from torch.distributions import normal, kl

# COMMAND ----------

# MAGIC %md
# MAGIC ---     

# COMMAND ----------

# DBTITLE 1,Quick test
import networkx as nx

edge_index = torch.tensor([[0, 1, 1, 2],
                           [1, 0, 2, 1]], dtype=torch.long)
x = torch.tensor([[-1], [0], [1]], dtype=torch.float)

data = torch_geometric.data.Data(x=x, edge_index=edge_index)
g = torch_geometric.utils.to_networkx(data, to_undirected=True)
nx.draw(g)

# COMMAND ----------

# MAGIC %md
# MAGIC ---      

# COMMAND ----------

# MAGIC %md 
# MAGIC
# MAGIC ### Test with [Pytorch Geometric Colab Example](https://pytorch-geometric.readthedocs.io/en/2.0.3/notes/colabs.html) -- [Node Classification with Graph Neural Networks](https://colab.research.google.com/drive/14OvFnAXggxB8vM4e8vSURUp1TaKnovzX?usp=sharing)
# MAGIC
# MAGIC <!-- https://colab.research.google.com/drive/14OvFnAXggxB8vM4e8vSURUp1TaKnovzX?usp=sharing -->

# COMMAND ----------

# DBTITLE 1,Helper function 
# Helper function for visualization.
%matplotlib inline
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

def visualize(h, color):
    z = TSNE(n_components=2).fit_transform(h.detach().cpu().numpy())

    plt.figure(figsize=(10,10))
    plt.xticks([])
    plt.yticks([])

    plt.scatter(z[:, 0], z[:, 1], s=70, c=color, cmap="Set2")
    plt.show()


# COMMAND ----------

# DBTITLE 1,Cora: citation network data
# MAGIC %md 
# MAGIC
# MAGIC "Cora dataset ([Yang et al. (2016)](https://arxiv.org/abs/1603.08861)) is a citation network where nodes represent documents. Each node is characterized by a 1433-dimensional bag-of-words feature vector. Two documents are connected if there exists a citation link between them." 
# MAGIC
# MAGIC **Semi-Supervised Learning**: Given a small subset of ground-truth labelled documents about their associated categories, can we **infer the categorical labels for the remaining documents**?

# COMMAND ----------

# DBTITLE 1,Download Citation Network Data:  
from torch_geometric.datasets import Planetoid
from torch_geometric.transforms import NormalizeFeatures

dataset = Planetoid(root='data/Planetoid', name='Cora', transform=NormalizeFeatures())

print()
print(f'Dataset: {dataset}:')
print('======================')
print(f'Number of graphs: {len(dataset)}')
print(f'Number of features: {dataset.num_features}')
print(f'Number of classes: {dataset.num_classes}')

data = dataset[0]  # Get the first graph object.

print()
print(data)
print('===========================================================================================================')

# Gather some statistics about the graph.
print(f'Number of nodes: {data.num_nodes}')
print(f'Number of edges: {data.num_edges}')
print(f'Average node degree: {data.num_edges / data.num_nodes:.2f}')
print(f'Number of training nodes: {data.train_mask.sum()}')
print(f'Training node label rate: {int(data.train_mask.sum()) / data.num_nodes:.2f}')
print(f'Has isolated nodes: {data.has_isolated_nodes()}')
print(f'Has self-loops: {data.has_self_loops()}')
print(f'Is undirected: {data.is_undirected()}')

# COMMAND ----------

# DBTITLE 1,Simple Multi-layer Perception Network (MLP) -- (shared weights across all nodes)

class MLP(torch.nn.Module):
    def __init__(self, hidden_channels):
        super().__init__()
        torch.manual_seed(12345)
        self.lin1 = Linear(dataset.num_features, hidden_channels)
        self.lin2 = Linear(hidden_channels, dataset.num_classes)

    def forward(self, x):
        x = self.lin1(x)
        x = x.relu()
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.lin2(x)
        return x

model = MLP(hidden_channels=16)
print(model)

# COMMAND ----------

# DBTITLE 1,Train a MLP
model = MLP(hidden_channels=16)
criterion = torch.nn.CrossEntropyLoss()  # Define loss criterion.
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)  # Define optimizer.

def train():
      model.train()
      optimizer.zero_grad()  # Clear gradients.
      out = model(data.x)  # Perform a single forward pass.
      loss = criterion(out[data.train_mask], data.y[data.train_mask])  # Compute the loss solely based on the training nodes.
      loss.backward()  # Derive gradients.
      optimizer.step()  # Update parameters based on gradients.
      return loss

def test():
      model.eval()
      out = model(data.x)
      pred = out.argmax(dim=1)  # Use the class with highest probability.
      test_correct = pred[data.test_mask] == data.y[data.test_mask]  # Check against ground-truth labels.
      test_acc = int(test_correct.sum()) / int(data.test_mask.sum())  # Derive ratio of correct predictions.
      return test_acc

for epoch in range(1, 201):
    loss = train()
    print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}')

# COMMAND ----------

# DBTITLE 1,MLP Test Accuracy
test_acc = test()
print(f'Test Accuracy: {test_acc:.4f}')

# COMMAND ----------

# DBTITLE 1,Train a Graph Neural Network (GNN) 
# Convert MLP to a GNN by swapping the torch.nn.Linear layers with PyG's GNN operators; leveraging a fixed normalization coefficient for each edge to make use of neighboring node information

from torch_geometric.nn import GCNConv

class GCN(torch.nn.Module):
    def __init__(self, hidden_channels):
        super().__init__()
        torch.manual_seed(1234567)
        self.conv1 = GCNConv(dataset.num_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, dataset.num_classes)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = x.relu()
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index)
        return x

model = GCN(hidden_channels=16)
print(model)

# COMMAND ----------

# DBTITLE 1,Visualize the N-dim node embeddings of untrained GCN network in 2D
model = GCN(hidden_channels=16)
model.eval()

out = model(data.x, data.edge_index)
visualize(out, color=data.y) 
#use of TSNE to embed our N-dimensional node embeddings onto a 2D plane.

# COMMAND ----------

# DBTITLE 1,Train GCN 
model = GCN(hidden_channels=16)
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

def train():
      model.train()
      optimizer.zero_grad()  # Clear gradients.
      out = model(data.x, data.edge_index)  # Perform a single forward pass.
      # make use of the node features x and the graph connectivity edge_index as input to GCN model
      loss = criterion(out[data.train_mask], data.y[data.train_mask])  # Compute the loss solely based on the training nodes.
      loss.backward()  # Derive gradients.
      optimizer.step()  # Update parameters based on gradients.
      return loss

def test():
      model.eval()
      out = model(data.x, data.edge_index)
      pred = out.argmax(dim=1)  # Use the class with highest probability.
      test_correct = pred[data.test_mask] == data.y[data.test_mask]  # Check against ground-truth labels.
      test_acc = int(test_correct.sum()) / int(data.test_mask.sum())  # Derive ratio of correct predictions.
      return test_acc


for epoch in range(1, 101):
    loss = train()
    print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}')

# COMMAND ----------

# DBTITLE 1,GCN Test Accuracy
test_acc = test()
print(f'Test Accuracy: {test_acc:.4f}')

# COMMAND ----------

# DBTITLE 1,Visualize embeddings of trained model
model.eval()

out = model(data.x, data.edge_index)
visualize(out, color=data.y)

# COMMAND ----------

# MAGIC %md
# MAGIC ---     

# COMMAND ----------

# DBTITLE 0,Additional example of graph network use case
from networkx_examples.plot_betweenness_centrality import *
btwcentrality_wormnet()
