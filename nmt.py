import tensorflow as tf
from tensorflow.python.layers import core as layers_core


class TrainingModel:
    def __init__(self, train_iterator, src_vocab_size, tgt_vocab_size, src_embed_size, tgt_embed_size, num_units, batch_size, max_gradient_norm, learning_rate):
        source, target_in, target_out, source_lengths, target_lengths = train_iterator.get_next()

        # Lookup embeddings
        embedding_encoder = tf.get_variable("embedding_encoder", [src_vocab_size, src_embed_size])
        encoder_emb_inp = tf.nn.embedding_lookup(embedding_encoder, source)
        embedding_decoder = tf.get_variable("embedding_decoder", [tgt_vocab_size, tgt_embed_size])
        decoder_emb_inp = tf.nn.embedding_lookup(embedding_decoder, target_in)

        # Build and run Encoder LSTM
        encoder_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units)
        encoder_outputs, encoder_state = tf.nn.dynamic_rnn(encoder_cell, encoder_emb_inp, sequence_length=source_lengths, dtype=tf.float32)

        # Build and run Decoder LSTM with TrainingHelper and output projection layer
        decoder_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units)
        projection_layer = layers_core.Dense(tgt_vocab_size, use_bias=False)
        helper = tf.contrib.seq2seq.TrainingHelper(decoder_emb_inp, sequence_length=target_lengths)
        decoder = tf.contrib.seq2seq.BasicDecoder(decoder_cell, helper, encoder_state, output_layer=projection_layer)
        outputs, _, _ = tf.contrib.seq2seq.dynamic_decode(decoder)
        logits = outputs.rnn_output

        # Calculate loss
        crossent = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=target_out, logits=logits)
        target_weights = tf.sequence_mask(target_lengths, maxlen=tf.shape(target_out)[1], dtype=logits.dtype)
        self.train_loss = tf.reduce_sum((crossent * target_weights) / batch_size)

        # Calculate and clip gradients
        params = tf.trainable_variables()
        gradients = tf.gradients(self.train_loss, params)
        clipped_gradients, _ = tf.clip_by_global_norm(gradients, max_gradient_norm)

        # Optimize model
        optimizer = tf.train.AdamOptimizer(learning_rate)
        self.update_step = optimizer.apply_gradients(zip(clipped_gradients, params))

    def train(self, sess):
        return sess.run([self.update_step, self.train_loss])