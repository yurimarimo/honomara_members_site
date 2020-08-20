import {config, dom, library} from '@fortawesome/fontawesome-svg-core';
import {faPen,faEdit,faTrashAlt} from '@fortawesome/free-solid-svg-icons';
library.add(faEdit);
library.add(faPen);
library.add(faTrashAlt);

dom.i2svg();
