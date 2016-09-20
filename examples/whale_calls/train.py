#!/usr/bin/env python
# ----------------------------------------------------------------------------
# Copyright 2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
import os
from neon import logger as neon_logger
from neon.util.argparser import NeonArgparser
from neon.optimizers import Adadelta
from neon.transforms import Misclassification
from neon.callbacks.callbacks import Callbacks
from network import create_network
from data import make_train_loader, make_val_loader

eval_config = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'whale_eval.cfg')
parser = NeonArgparser(__doc__, default_config_files=[eval_config])
args = parser.parse_args()

model, cost_obj = create_network()

assert 'train' in args.manifest, "Missing train manifest"
assert 'val' in args.manifest, "Missing val manifest"

train = make_train_loader(args.manifest['train'], model.be, noise_file=args.manifest.get('noise'))

neon_logger.display('Performing train and test in validation mode')
val = make_val_loader(args.manifest['val'], model.be)
metric = Misclassification()

model.fit(dataset=train,
          cost=cost_obj,
          optimizer=Adadelta(),
          num_epochs=args.epochs,
          callbacks=Callbacks(model, eval_set=val, metric=metric, **args.callback_args))

neon_logger.display('Misclassification error = %.1f%%' % (model.eval(val, metric=metric) * 100))
