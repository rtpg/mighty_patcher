#include <stdlib.h>
#include "Python.h"

static PyObject* give_type_name(PyObject* self, PyObject* obj){
        return PyUnicode_FromString(obj->ob_type->tp_name);
}


static PyObject* replace_dict(PyObject* self, PyObject* args){
    // TODO garabage collection
    PyDictObject* fst;
    PyDictObject* snd;

    if(!PyArg_UnpackTuple(args, "ref", 2, 2, &fst, &snd)){
        return PyUnicode_FromString("failed unpack");
    }

    fst->ma_keys = snd->ma_keys;
    fst->ma_used = snd->ma_used;
    fst->ma_values = snd->ma_values;
    fst->ma_version_tag = snd->ma_version_tag;
    fst->ob_base = snd->ob_base;

    return PyUnicode_FromString("success");
}

#define copy_old(field) old_fst->field = fst->field
#define copy_snd(field) fst->field = snd->field

static PyObject* replace_func(PyObject* self, PyObject* args){
    /**
     * Replace the contents of first with the contents of second, and return the old contents
     * of first (this should make reference counts correct)
     */
    // TODO garbage collection
    PyFunctionObject* fst;
    PyFunctionObject* snd;
    if(!PyArg_UnpackTuple(args, "ref", 2,2, &fst, &snd)){
        return PyUnicode_FromString("failed unpack");
    }

    PyFunctionObject* old_fst = PyObject_GC_New(PyFunctionObject, &PyFunction_Type);
    copy_old(func_code);
    copy_old(func_defaults);
    copy_old(func_kwdefaults);
    copy_old(func_closure);
    copy_old(func_doc);
    copy_old(func_name);
    copy_old(func_dict);
    copy_old(func_module);
    copy_old(func_annotations);
    copy_old(func_qualname);
    copy_old(func_globals);

    PyObject_GC_Track(old_fst);
//    old_fst->func_code = fst->func_code;
//    old_fst->func_defaults = fst->func_defaults;
//    old_fst->func_kwdefaults = fst->func_kwdefaults;
//    old_fst->func_closure = fst->func_closure;
//    old_fst->func_doc = fst->func_doc;
//    old_fst->func_name = fst->func_name;
//    old_fst->func_dict = fst->func_dict;
//    old_fst->func_globals = fst->func_globals;
//    fst->ob_base = snd->ob_base;

    copy_snd(func_code);
    Py_XINCREF(fst->func_code);
    copy_snd(func_defaults);
//    fst->func_defaults = snd->func_defaults;
    Py_XINCREF(fst->func_defaults);
    copy_snd(func_kwdefaults);
    Py_XINCREF(fst->func_kwdefaults);
    copy_snd(func_closure);
    Py_XINCREF(fst->func_closure);
    copy_snd(func_doc);
    Py_XINCREF(fst->func_doc);
    copy_snd(func_name);
    Py_XINCREF(fst->func_name);
    copy_snd(func_dict);
    Py_XINCREF(fst->func_dict);
    // TODO figure out weakreflist issues
//    copy_snd(func_weakreflist);
//    Py_XINCREF(fst->func_weakreflist);
    // Hack to avoid segfault
    snd->func_weakreflist = NULL;
    copy_snd(func_module);
    Py_XINCREF(fst->func_module);
    copy_snd(func_annotations);
    Py_XINCREF(fst->func_annotations);
    copy_snd(func_qualname);
    Py_XINCREF(fst->func_qualname);
    copy_snd(func_globals);
    Py_XINCREF(fst->func_globals);

    // THIS IS A BUG
    // this totally memory leaks everything but the stuff I end up touching here
    // can't get thrown away without some weakreference stuff blowing up
    //
    // [To the tune of that one song]
    // I add reference counts on all the things
    // I don't even bother to read any spec
    // I segfault on GC collections all the time
    // So I just turn it all off and leak away
    // I DON'T CARE
    // I LOVE IT
    //
    Py_XINCREF(fst);
    Py_XINCREF(snd);
    Py_XINCREF(old_fst);
    return old_fst;
}

static PyObject* replace_type(PyObject* self, PyObject* args){
    PyTypeObject* fst;
    PyTypeObject* snd;

    if(!PyArg_UnpackTuple(args, "ref", 2,2, &fst, &snd)){
        return PyUnicode_FromString("failed unpack");
    }

    PyTypeObject* old_fst = PyObject_GC_New(PyTypeObject, &PyType_Type);

    // MEMORY LEAK HERE, this is a const char*
    copy_old(tp_name);
    copy_old(tp_basicsize);
    copy_old(tp_itemsize);
    copy_old(tp_dealloc);
    copy_old(tp_print);
    copy_old(tp_getattr);
    copy_old(tp_setattr);
    copy_old(tp_as_async);
    copy_old(tp_repr);
    copy_old(tp_as_number);
    copy_old(tp_as_sequence);
    copy_old(tp_as_mapping);
    copy_old(tp_hash);
    copy_old(tp_call);
    copy_old(tp_str);
    copy_old(tp_getattro);
    copy_old(tp_setattro);
    copy_old(tp_as_buffer);
    copy_old(tp_flags);
    copy_old(tp_doc);
    copy_old(tp_traverse);
    copy_old(tp_clear);
    copy_old(tp_richcompare);
    copy_old(tp_weaklistoffset);
    copy_old(tp_iter);
    copy_old(tp_iternext);
    copy_old(tp_methods);
    copy_old(tp_members);
    copy_old(tp_getset);
    copy_old(tp_base);
    copy_old(tp_dict);
    copy_old(tp_descr_get);
    copy_old(tp_descr_set);
    copy_old(tp_dictoffset);
    copy_old(tp_init);
    copy_old(tp_alloc);
    copy_old(tp_new);
    copy_old(tp_free);
    copy_old(tp_is_gc);
    copy_old(tp_bases);
    copy_old(tp_mro);
    copy_old(tp_cache);
    copy_old(tp_subclasses);
    copy_old(tp_weaklist);
    copy_old(tp_del);
    copy_old(tp_version_tag);
    copy_old(tp_finalize);

    // MEMORY LEAK HERE, this is a const char*
    copy_snd(tp_name);
    copy_snd(tp_basicsize);
    copy_snd(tp_itemsize);
    copy_snd(tp_dealloc);
    copy_snd(tp_print);
    copy_snd(tp_getattr);
    copy_snd(tp_setattr);
    copy_snd(tp_as_async);
    copy_snd(tp_repr);
    copy_snd(tp_as_number);
    copy_snd(tp_as_sequence);
    copy_snd(tp_as_mapping);
    copy_snd(tp_hash);
    copy_snd(tp_call);
    copy_snd(tp_str);
    copy_snd(tp_getattro);
    copy_snd(tp_setattro);
    copy_snd(tp_as_buffer);
    copy_snd(tp_flags);
    copy_snd(tp_doc);
    copy_snd(tp_traverse);
    copy_snd(tp_clear);
    copy_snd(tp_richcompare);
    copy_snd(tp_weaklistoffset);
    copy_snd(tp_iter);
    copy_snd(tp_iternext);
    copy_snd(tp_methods);
    copy_snd(tp_members);
    copy_snd(tp_getset);
    copy_snd(tp_base);
    copy_snd(tp_dict);
    copy_snd(tp_descr_get);
    copy_snd(tp_descr_set);
    copy_snd(tp_dictoffset);
    copy_snd(tp_init);
    copy_snd(tp_alloc);
    copy_snd(tp_new);
    copy_snd(tp_free);
    copy_snd(tp_is_gc);
    copy_snd(tp_bases);
    copy_snd(tp_mro);
    copy_snd(tp_cache);
    copy_snd(tp_subclasses);
    copy_snd(tp_weaklist);
    copy_snd(tp_del);
    copy_snd(tp_version_tag);
    copy_snd(tp_finalize);

    Py_XINCREF(fst);
    Py_XINCREF(snd);
    Py_XINCREF(old_fst);
    return old_fst;
}


static PyObject* replace_cfunction(PyObject* self, PyObject* args){
    PyCFunctionObject* fst;
    PyCFunctionObject* snd;

    if(!PyArg_UnpackTuple(args, "ref", 2,2, &fst, &snd)){
        return PyUnicode_FromString("failed unpack");
    }

    PyCFunctionObject* old_fst = PyObject_GC_New(PyCFunctionObject, &PyCFunction_Type);
    copy_old(m_ml);
    copy_old(m_self);
    copy_old(m_module);
    copy_old(m_weakreflist);

    copy_snd(m_ml);
    copy_snd(m_self);
    copy_snd(m_module);
    copy_snd(m_weakreflist);

    Py_XINCREF(fst);
    Py_XINCREF(snd);
    Py_XINCREF(old_fst);
    return old_fst;
}
static struct PyMethodDef module_functions[] = {
    {"give_type_name", give_type_name, METH_O, NULL},
    {"replace_dict", replace_dict, METH_VARARGS, NULL},
    {"replace_func", replace_func, METH_VARARGS, NULL},
    {"replace_type", replace_type, METH_VARARGS, NULL},
    {"replace_cfunction", replace_cfunction, METH_VARARGS, NULL},
    {NULL, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "mighty_patcher._better_mocking", /* m_name */
    NULL,             /* m_doc */
    -1,               /* m_size */
    module_functions, /* m_methods */
    NULL,             /* m_reload */
    NULL,             /* m_traverse */
    NULL,             /* m_clear */
    NULL,             /* m_free */
};

static PyObject* moduleinit(void) {
    PyObject *module;

    module = PyModule_Create(&moduledef);

    if (module == NULL)
        return NULL;

    return module;
}

PyMODINIT_FUNC PyInit__better_mocking(void) {
    return moduleinit();
}

