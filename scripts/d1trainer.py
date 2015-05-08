#!/usr/bin/env python3.4

import sys
import ConfigParser
import ihmm
import logging
import numpy as np
import pdb
import os

def main(argv):
    if len(argv) < 1:
        sys.stderr.write("One required argument: <Config file>\n")
        sys.exit(-1)

    config = ConfigParser.ConfigParser()
    config.read(argv[0])
    
    input_file = config.get('io', 'input_file')
    out_dir = config.get('io', 'output_dir')
    
    if not os.path.exists(out_dir):
        sys.stderr.write("Creating non-existent output directory.")
        os.makedirs(out_dir)

    ## Read in input file to get sequence for X
    (pos_seq, word_seq) = read_input_file(input_file)
    num_types = max(map(max,word_seq)) + 1
    
    params = read_params(config)
    
    params['h'] = init_emission_base(num_types)
    
    (samples, stats) = ihmm.sample_beam(word_seq, params, lambda x: write_output(x, None, config))
    
    write_output(samples[-1], stats, config)        

def read_params(config):
    params = {}
    for (key, val) in config.items('params'):
        #logging.debug("assigning params key val pair (%s, %s)", key, val)
        params[key] = val
    
    return params

def init_emission_base(size):
    ## Uniform distribution:
    H = np.zeros((1,size)) + 0.01
    return H

def read_input_file(filename):
    pos_seqs = list()
    token_seqs = list()
    f = open(filename, 'r')
    for line in f:
        pos_seq = list()
        token_seq = list()
        for token in line.split():
            if "/" in token:
                (pos, token) = token.split("/")
            else:
                pos = 0 
        
            pos_seq.append(int(pos))
            token_seq.append(int(token))

        pos_seqs.append(pos_seq)
        token_seqs.append(token_seq)
    
    return (pos_seqs, token_seqs)

def write_output(sample, stats, config):
#    last_sample = samples[-1]
    models = sample.models
    
    output_dir = config.get('io', 'output_dir')
    with open(output_dir + "/config.ini", 'w') as configfile:
        config.write(configfile)

    dict_file = config.get('io', 'dict_file')
    word_dict = dict()
    if dict_file != None:
        f = open(dict_file, 'r')
        for line in f:
            #pdb.set_trace()
            (word, index) = line.rstrip().split(" ")
            word_dict[int(index)] = word
    
    write_model(models.lex.dist, output_dir + "/p_lex_given_pos%d.txt" % sample.iter, word_dict)
    write_model(models.pos.dist, output_dir + "/p_pos_given_b_%d.txt" % sample.iter, condPrefix="AWA", outcomePrefix="POS")
    write_model(models.cont.dist, output_dir + "/p_awa_given_b+g%d.txt" % sample.iter,
    condPrefix="BG", outcomePrefix="AWA")
    write_model(models.start.dist, output_dir + "/p_awa_given_a%d.txt" % sample.iter,
    condPrefix="AA", outcomePrefix="AWA")
    write_model(models.act.dist, output_dir + "/p_act_given_a%d.txt" % sample.iter,
    condPrefix="ACT", outcomePrefix="ACT")
    write_model(models.root.dist, output_dir + "/p_act_given_g%d.txt" %sample.iter,
    condPrefix="POS", outcomePrefix="ACT")
    
    write_last_sample(sample, output_dir + "/last_sample%d.txt" % sample.iter)
    
def write_model(dist, out_file, word_dict=None, condPrefix="", outcomePrefix=""):
    f = open(out_file, 'w')
    
    for lhs in range(0,dist.shape[0]):
        for rhs in range(1,dist.shape[1]):
            #pdb.set_trace()
            if word_dict == None:
                f.write("P( %s%d | %s%d ) = %f \n" % (outcomePrefix, rhs, condPrefix, lhs, dist[lhs][rhs]))
            else:
                f.write("P( %s | %d ) = %f \n" % (word_dict[rhs], lhs, dist[lhs][rhs]))
                
    f.close()

def write_last_sample(sample, out_file):
    f = open(out_file, 'w')
    #pdb.set_trace()
    for sent_state in sample.hid_seqs:
        state_str = str(list(map(lambda x: x.str(), sent_state)))
        f.write(state_str)
        f.write('\n')
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])

