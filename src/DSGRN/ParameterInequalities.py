# ParameterInequalities.py
# Marcio Gameiro
# 2020-09-13
# MIT LICENSE

import DSGRN
import numpy as np

def hex2partial(hex_code, n_inputs, n_outputs):
    # Computes the partial order corresponding to a given hex code
    # This code is probably not optimized as it is used only for testing

    n_bits = n_outputs * (2**n_inputs) # number of bits
    fmt = '0' + str(n_bits) + 'b' # bit code format
    par_bit_code = format(int(hex_code, 16), fmt) # get the parameter bit code

    par_bit_array = list(reversed(np.fromiter(map(int, par_bit_code), dtype=int))) # array of bit codes
    # transform into matrix using column-major order (Fortran-like index ordering)
    par_bit_matrix = np.reshape(par_bit_array, (n_outputs, -1), order='F') # matrix of bit codes

    partial_order = [] # partial order list
    total_order_vals = list(range(2**n_inputs)) # values used in total order

    for row_indx, row in enumerate(par_bit_matrix): # for each row
        for col_indx, bit_val in enumerate(row): # for each column
            if (bit_val == 0) and (col_indx in total_order_vals): # if bit==0 and have not yet added col_indx
                total_order_vals.remove(col_indx) # remove from list of values not yet added
                partial_order.append(col_indx) # add value to the list
        partial_order.append(-(n_outputs - row_indx)) # add negative value for threshold

    partial_order.extend(total_order_vals) # add remaning values to list

    return partial_order

def factor_graph_inequalities(parameter_graph, par_index, node):
    # Given a parameter index and a network node returns the
    # parameter inequalities of the factor graph corresponding
    # to this node.
    parameter = parameter_graph.parameter(par_index)
    # Get inputs and outputs to node
    inputs = parameter_graph.network().inputs(node)
    outputs = parameter_graph.network().outputs(node)
    # Get number of inputs and outputs
    n_inputs = len(inputs)
    n_outputs = len(outputs)
    # Get factor graph hex code
    hex_code = parameter.logic()[node].hex()
    # Compute partial order corresponding to hex code
    partial_order = hex2partial(hex_code, n_inputs, n_outputs)

    def threshold_str(source_node, original_edge_index):
        # Given a source node and an edge index returns a
        # string for the threshold corresponding to the
        # out edge from source to outputs[edge_index] after
        # applying the order parameter permutation to edge_index.
        #
        # Get source node name
        source_name = parameter_graph.network().name(source_node)
        # Apply order parameter permutation to original_edge_index
        edge_index = parameter.order()[source_node](original_edge_index)
        # Get target node and name
        target = outputs[edge_index]
        target_name = parameter_graph.network().name(target)
        # Get count of target before edge_index position (instance)
        instance = outputs[:edge_index].count(target)
        # Get instances of (possibly multiple) input edges (not used here)
        # input_instances = parameter_graph.network().input_instances(target)
        thres_str = 'T[' + source_name + '->' + target_name + ', ' + str(instance) + ']'
        return thres_str

    # Make string for a partial order term
    def partial_order_term_str(p, source_node):
        if p < 0: # Return string for threshold
            # Get original edge index (out edge order)
            # This is the order before permutation
            original_edge_index = n_outputs + p
            return threshold_str(source_node, original_edge_index)
        # Return string for polynomial
        return 'p' + str(p)

    # Get node name
    node_name = parameter_graph.network().name(node)
    # Make inequalities string
    inequalities = node_name + ': '
    first = True
    for p in partial_order:
        # Get partial order term string
        p_str = partial_order_term_str(p, node)
        if first:
            inequalities += '(' + p_str
            first = False
        else:
            inequalities += ', ' + p_str
    inequalities += ')'

    return inequalities

def parameter_inequalities(parameter_graph, par_index):
    D = parameter_graph.dimension()
    # Get parameter inequalities
    parameter_ineqs = []
    for d in range(D):
        # Get inequalities for each factor graph
        factor_ineqs = factor_graph_inequalities(parameter_graph, par_index, d)
        parameter_ineqs.append(factor_ineqs)
    return parameter_ineqs
