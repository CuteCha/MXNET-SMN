from mxnet import init
import mxnet as mx
from mxnet.gluon import nn
from gensim.models.word2vec import Word2Vec
from PreProcess import WordVecs
import numpy as np
from mxnet import nd
from mxnet.gluon import rnn
import pickle
from mxnet import gluon
from mxnet import autograd

batch_size = 1000
ctx = mx.gpu(0)
#136334x200 shape for word embedding
#Load data
max_word_per_utterence = 50
dataset = r"train"
x = pickle.load(open(dataset,"rb"),encoding='utf-8')
revs, wordvecs, max_l = x[0], x[1], x[2]

max_turn = 10
def get_idx_from_sent_msg(sents, word_idx_map, max_l=50,mask = False):
    """
    Transforms sentence into a list of indices. Pad with zeroes.
    """
    turns = []
    for sent in sents.split('_t_'):
        x = [0] * max_l
        words = sent.split()
        length = len(words)
        for i, word in enumerate(words):
            if max_l - length + i < 0: continue
            if word in word_idx_map:
                x[max_l - length + i] = word_idx_map[word]

        turns.append(x)

    final = [0.] * (max_l  * max_turn)
    for i in range(max_turn):
        if max_turn - i <= len(turns):
            for j in range(max_l ):
                final[i*(max_l) + j] = turns[-(max_turn-i)][j]
    return final

def get_idx_from_sent(sent, word_idx_map, max_l=50,mask = False):
    """
    Transforms sentence into a list of indices. Pad with zeroes.
    """
    x = [0] * max_l
    x_mask = [0.] * max_l
    words = sent.split()
    length = len(words)
    for i, word in enumerate(words):
        if max_l - length + i < 0: continue
        if word in word_idx_map:
            x[max_l - length + i] = word_idx_map[word]

    return x

def get_data(raw_data,word_idx_map,batch_size,max_l,val_size=0):
    X,y,X_val,y_val = np.zeros((999000,550)),[],[],[]
    i = 0
    t = 0
    for rev in raw_data:
        
        
        sent = get_idx_from_sent_msg(rev["m"], word_idx_map, max_l, False)
        sent += get_idx_from_sent(rev["r"], word_idx_map, max_l, False)
        if(i<val_size):
            print(i)
            i = i + 1
            X_val.append(sent)
            y_val.append(int(rev["y"]))
        else:
            X[t] = sent
            t = t + 1
            if(t%100==0):
                print(t)
            y.append(int(rev["y"]))
    print(X[10000])
    X = nd.array(X,ctx =ctx)
    y = nd.array(y,ctx = ctx)
    print("get data")
    X_val = nd.array(X_val,ctx=ctx)
    y_val = nd.array(y_val,ctx=ctx)
#    mx.ndarray.reshape(y_val,shape=(batch_size,1))
    train_dataset = gluon.data.ArrayDataset(X, y)
    train_data_iter = gluon.data.DataLoader(train_dataset, batch_size, shuffle=True)
    val_dataset = gluon.data.ArrayDataset(X_val,y_val)
    val_data_iter = gluon.data.DataLoader(val_dataset,batch_size,shuffle=True)
    return train_data_iter,val_data_iter

class SMN_Last(nn.Block):
    def __init__(self,**kwargs):
        super(SMN_Last,self).__init__(**kwargs)
        with self.name_scope():
            self.Embed = nn.Embedding(136334,200)
            self.conv = nn.Conv2D(channels=8, kernel_size=3, activation='relu')
            self.pooling = nn.MaxPool2D(pool_size=3, strides=3)
            self.mlp_1 = nn.Dense(units=50,activation='tanh',flatten=True)
            self.gru_1 = rnn.GRU(hidden_size=50,layout='NTC')
            self.gru_2 = rnn.GRU(layout='NTC',hidden_size=50)
            self.mlp_2 = nn.Dense(units=2,flatten=False)
            self.W = mx.nd.ones((50,50),ctx=ctx)
    def forward(self,x):
        u_0,u_1,u_2,u_3,u_4,u_5,u_6,u_7,u_8,u_9,r=x[:,0:50],x[:,50:100],x[:,100:150],x[:,150:200],x[:,200:250],x[:,250:300],x[:,300:350],x[:,350:400],x[:,400:450],x[:,450:500],x[:,500:550]

        u_0 = self.Embed(u_0)
        u_1 = self.Embed(u_1)
        u_2 = self.Embed(u_2)
        u_3 = self.Embed(u_3)
        u_4 = self.Embed(u_4)
        u_5 = self.Embed(u_5)
        u_6 = self.Embed(u_6)
        u_7 = self.Embed(u_7)
        u_8 = self.Embed(u_8)
        u_9 = self.Embed(u_9)
        r = self.Embed(r)
        h_0 = nd.zeros((1,batch_size,50),ctx = ctx)

        gru_u_0,_ = self.gru_1(u_0, h_0)
        gru_u_1,_ = self.gru_1(u_1, h_0)
        gru_u_2,_ = self.gru_1(u_2, h_0)
        gru_u_3,_ = self.gru_1(u_3, h_0)
        gru_u_4,_ = self.gru_1(u_4, h_0)
        gru_u_5,_ = self.gru_1(u_5, h_0)
        gru_u_6,_ = self.gru_1(u_6, h_0)
        gru_u_7,_ = self.gru_1(u_7, h_0)
        gru_u_8,_ = self.gru_1(u_8, h_0)
        gru_u_9,_ = self.gru_1(u_9, h_0)
        gru_r,_ = self.gru_1(r, h_0)

        #_,gru_u_0 = self.gru_1(u_0,h_0)
        #_,gru_u_1 = self.gru_1(u_1,h_0)
        #_,gru_u_2 = self.gru_1(u_2,h_0)
        #_,gru_u_3 = self.gru_1(u_3,h_0)
        #_,gru_u_4 = self.gru_1(u_4,h_0)
        #_,gru_u_5 = self.gru_1(u_5,h_0)
        #_,gru_u_6 = self.gru_1(u_6,h_0)
        #_,gru_u_7 = self.gru_1(u_7,h_0)
        #_,gru_u_8 = self.gru_1(u_8,h_0)
        #_,gru_u_9 = self.gru_1(u_9,h_0)
        #_,gru_r = self.gru_1(r,h_0)

        #gru_u_0 = gru_u_0[0]
        #gru_u_1 = gru_u_1[0]
        #gru_u_2 = gru_u_2[0]
        #gru_u_3 = gru_u_3[0]
        #gru_u_4 = gru_u_4[0]
        #gru_u_5 = gru_u_5[0]
        #gru_u_6 = gru_u_6[0]
        #gru_u_7 = gru_u_7[0]
        #gru_u_8 = gru_u_8[0]
        #gru_u_9 = gru_u_9[0]
        #gru_r = gru_r[0]

        #gru_u_0 = mx.nd.transpose(gru_u_0, axes=(1, 2, 0))
        #gru_u_1 = mx.nd.transpose(gru_u_1, axes=(1, 2, 0))
        #gru_u_2 = mx.nd.transpose(gru_u_2, axes=(1, 2, 0))
        #gru_u_3 = mx.nd.transpose(gru_u_3, axes=(1, 2, 0))
        #gru_u_4 = mx.nd.transpose(gru_u_4, axes=(1, 2, 0))
        #gru_u_5 = mx.nd.transpose(gru_u_5, axes=(1, 2, 0))
        #gru_u_6 = mx.nd.transpose(gru_u_6, axes=(1, 2, 0))
        #gru_u_7 = mx.nd.transpose(gru_u_7, axes=(1, 2, 0))
        #gru_u_8 = mx.nd.transpose(gru_u_8, axes=(1, 2, 0))
        #gru_u_9 = mx.nd.transpose(gru_u_9, axes=(1, 2, 0))


        r_t = mx.nd.transpose(r,axes=(0,2,1))
        gru_r_t = mx.nd.transpose(gru_r,axes=(0, 2, 1))

        M01 = nd.batch_dot(u_0,r_t)
        M02 = nd.batch_dot(nd.dot(gru_u_0,self.W),gru_r_t)
        M11 = nd.batch_dot(u_1,r_t)
        M12 = nd.batch_dot(nd.dot(gru_u_1,self.W),gru_r_t)
        M21 = nd.batch_dot(u_2,r_t)
        M22 = nd.batch_dot(nd.dot(gru_u_2,self.W),gru_r_t)
        M31 = nd.batch_dot(u_3,r_t)
        M32 = nd.batch_dot(nd.dot(gru_u_3,self.W),gru_r_t)
        M41 = nd.batch_dot(u_4,r_t)
        M42 = nd.batch_dot(nd.dot(gru_u_4,self.W),gru_r_t)
        M51 = nd.batch_dot(u_5,r_t)
        M52 = nd.batch_dot(nd.dot(gru_u_5,self.W),gru_r_t)
        M61 = nd.batch_dot(u_6,r_t)
        M62 = nd.batch_dot(nd.dot(gru_u_6,self.W),gru_r_t)
        M71 = nd.batch_dot(u_7,r_t)
        M72 = nd.batch_dot(nd.dot(gru_u_7,self.W),gru_r_t)
        M81 = nd.batch_dot(u_8,r_t)
        M82 = nd.batch_dot(nd.dot(gru_u_8,self.W),gru_r_t)
        M91 = nd.batch_dot(u_9,r_t)
        M92 = nd.batch_dot(nd.dot(gru_u_9,self.W),gru_r_t)

#input to conv layer
        M0 = nd.stack(M01, M02, axis=1)
        M1 = nd.stack(M11, M12, axis=1)
        M2 = nd.stack(M21, M22, axis=1)
        M3 = nd.stack(M31, M32, axis=1)
        M4 = nd.stack(M41, M42, axis=1)
        M5 = nd.stack(M51, M52, axis=1)
        M6 = nd.stack(M61, M62, axis=1)
        M7 = nd.stack(M71, M72, axis=1)
        M8 = nd.stack(M81, M82, axis=1)
        M9 = nd.stack(M91, M92, axis=1)

#output of conv

        conv_out_0 = self.mlp_1(self.pooling(self.conv(M0)))
        conv_out_1 = self.mlp_1(self.pooling(self.conv(M1)))
        conv_out_2 = self.mlp_1(self.pooling(self.conv(M2)))
        conv_out_3 = self.mlp_1(self.pooling(self.conv(M3)))
        conv_out_4 = self.mlp_1(self.pooling(self.conv(M4)))
        conv_out_5 = self.mlp_1(self.pooling(self.conv(M5)))
        conv_out_6 = self.mlp_1(self.pooling(self.conv(M6)))
        conv_out_7 = self.mlp_1(self.pooling(self.conv(M7)))
        conv_out_8 = self.mlp_1(self.pooling(self.conv(M8)))
        conv_out_9 = self.mlp_1(self.pooling(self.conv(M9)))
        #TODO:figure out why the conv output is tuple?
#concat as input to gru_2
        Concat_conv_out = nd.stack(conv_out_0,conv_out_1,conv_out_2,conv_out_3,
                                   conv_out_4,conv_out_5,conv_out_6,conv_out_7,
                                   conv_out_8,conv_out_9,axis=1)
#output of gru_2
        h_1 = nd.zeros((1,batch_size,50),ctx=ctx)
        _,gru_out = self.gru_2(Concat_conv_out,h_1)
#output of mlp(yhat)
        y_hat = self.mlp_2(gru_out[0])
        return y_hat[0]

#Train Model
SMN = SMN_Last()
SMN.initialize(ctx=mx.gpu())
word2vec = (nd.array(wordvecs.W)).copyto(mx.gpu(0))
#print(word2vec)
class MyInit(init.Initializer):
	def __init__(self):
		super(MyInit,self).__init__()
		self._verbose = True
	def _init_weight(self, _,arr):
		word2vec
#params = SMN.collect_params()
#print(params)
#params['smn_last0_embedding0_weight'].initialize(force_reinit = True,ctx = mx.cpu())
#params['smn_last0_embedding0_weight'].initialize(MyInit(),force_reinit = True,ctx = ctx)
#SMN.Embed.weight.set_data(word2vec)

train_iter,val_iter = get_data(revs,wordvecs.word_idx_map,batch_size,max_l=50,val_size = 1000)

max_epoch = 50

softmax_cross_entropy = gluon.loss.SoftmaxCrossEntropyLoss()
trainer = gluon.Trainer(SMN.collect_params(), 'adam', {'learning_rate': 0.001})

for test_data, ground_truth in val_iter:
    t_data,t_label = test_data,ground_truth

for epoch in range(max_epoch):
    train_loss = 0.
    train_acc = 0.
    for data, label in train_iter:
        with autograd.record():
            output = SMN(data)
            loss = softmax_cross_entropy(output, nd.array(label,ctx=ctx))
        loss.backward()
        trainer.step(batch_size)
        print("loss:")
        #print(np.sum(label.asnumpy()))
        print(nd.mean(loss).asscalar())
        print("acc:")
        acc = mx.metric.Accuracy()
        test_y_hat = SMN(t_data)
       # print("--------")
       #  print(test_y_hat)
        test_label = nd.array(t_label,ctx=ctx)
        acc.update(preds = [test_y_hat],labels = [test_label])
        print(acc.get())
       # acc = None
        #for test_data, ground_truth in val_iter:
           # test_y_hat = SMN(test_data)
           # print(test_y_hat.shape)
           # acc = mx.metric.Accuracy()
            #test_y_hat = nd.array(test_y_hat.asnumpy().reshape((2,1000)))
           # test_label = nd.array(ground_truth,ctx=ctx)
            #test_label = nd.array(test_label.asnumpy(),ctx = ctx)
            #print(test_label)
           # acc.update(preds = [test_y_hat],labels = [test_label])
           # print(acc.get())
           # break
        train_loss += nd.mean(loss).asscalar()
        #train_acc += utils.accuracy(output, label)
        train_acc = 0
    #test_acc = utils.evaluate_accuracy(test_data, net)
    test_acc = 0
    print("Epoch %d. Loss: %f, Train acc %f, Test acc %f" % (
        epoch, train_loss/len(train_iter), train_acc/len(train_iter), test_acc))
