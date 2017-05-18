# diffbuff

Differenciable protocol buffers, the first attempt at implementation.

## Status

This project has turned out to be far much more difficult than I estimated. There
is a partial implementation of the X-Diff -algorithm in the diffbuff/treediff.py
module. Other than that, this goes into the abandoned bin.

## Implementation schedule

The implementation falls across the ladder:

 * Not implemented
 * Testing required
 * Alpha

When all subsystems reach this point, the milestone Alpha is reached. After
this point an incubation period is started, which will take 2-6 months. This is
the time reserved for writing and revising the specification. It is required so
that we hopefully avoid the "diffbuff2" or "diffbuff3".

### Testing required

 * Wire format

### Yet to be implemented

 * Diff on buffers
 * Pretty printing without a schema
 * Schema on schemas
 * Schema on edit scripts
 * Schema language and a compiler
 * Pretty printing with a schema
 * Python API on working with diffbuffs
 * Diffbuff-to-C compiler

### Rationale on the implementation order

The priority is on the defining qualities of the format. Without its defining
qualities there would be nothing that differenciates diffbuff from protobuf.

## Type support list

 1. Bit vectors
 1. Enumeration values, Messages, Union types, false, null, true
 1. IEEE 754-2008 floating point values, (base 2, base 10), extendable precision
 1. Lists, Maps, Sets
 1. Packed flat records
 1. Packed messages of uniform type
 1. Unicode strings
 1. Variable size signed and unsigned numbers
 1. Vectors, Matrices, Tensors
 1. Sparse matrices

The support is defined in tiers, and modules, so that people implementing the
features can report the tier and the modules they support. The exact grouping
is to be decided.

