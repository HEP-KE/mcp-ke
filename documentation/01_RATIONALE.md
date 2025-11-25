# MCP-KE: Design Rationale

## Overview

**MCP-KE** (Model Context Protocol - Knowledge Engineering) is an MCP server that provides AI-powered tools for cosmological data analysis. It implements the **"tools-as-agents"** pattern, exposing both simple computational tools and complex multi-agent workflows through a uniform MCP interface.

![Abstract Architecture](abstract_architecture.png)

The abstract architecture diagram shows the high-level tool server pattern that MCP-KE implements.

## Motivation

### The Problem

Modern cosmology analysis requires:
1. **Domain expertise**: Understanding CLASS (Cosmic Linear Anisotropy Solving System), power spectrum analysis, observational data formats
2. **Multi-step workflows**: Load data → compute models → analyze results → create visualizations
3. **Integration complexity**: Connecting scientific computing libraries with AI agents

Traditional approaches require either:
- Writing extensive custom code for each analysis task
- Deep knowledge of cosmology software and Python scientific stack
- Manual orchestration of multi-step analysis pipelines

### The Solution

MCP-KE provides a **tool server** that:
- Exposes 23 specialized tools via MCP protocol
- Allows any MCP client (Claude Desktop, custom agents) to perform cosmology analysis
- Encapsulates domain expertise in reusable tool functions
- Provides both **atomic tools** (simple functions) and **agent tools** (multi-agent workflows)

## Design Rationale

### Why MCP?

**Pros**:
- Standard protocol for LLM-tool communication
- Supported by major AI platforms (Anthropic, etc.)
- Language-agnostic (JSON-RPC over stdio)
- Secure subprocess isolation
- Simple deployment (no servers, ports, or networking)

**Cons**:
- Still evolving standard
- Limited to stdio communication (no streaming large data)
- Requires client support

**Alternative Considered**: REST API
- Would require managing server lifecycle, ports, authentication
- More complex deployment
- MCP is simpler for local development and Claude Desktop integration

### Why Smolagents?

**smolagents** is Hugging Face's lightweight agent framework:
- Simple `@tool` decorator
- Built-in `CodeAgent` for multi-step reasoning
- Support for managed sub-agents (hierarchical orchestration)
- LLM-agnostic (works with any OpenAI-compatible API)

**Alternative Considered**: LangChain
- More features but heavier dependencies
- smolagents is more focused and easier to understand
- Better fit for tool-centric design

### Why Two-Tier Tool System?

**Domain Tools**:
- Composable primitives
- Testable in isolation
- Reusable across workflows
- Low latency

**Agent Tools**:
- Handle complex, multi-step workflows
- Reduce client orchestration burden
- Encapsulate domain expertise
- Higher latency but much more capable

**Benefit**: Clients can choose appropriate abstraction level

### Why File-Based Agent Communication?

**Problem**: Passing large NumPy arrays between agents overflows context

**Solution**: Agents pass file paths, not data
- File: `/path/to/out/k_theory.npy`
- Next agent loads with `load_array`

**Pros**:
- Bounded context usage
- Persistent intermediate results (debugging, inspection)
- Clear data lineage

**Cons**:
- Requires shared filesystem
- Manual cleanup needed

**Alternative Considered**: Structured message passing
- Would require serialization/deserialization
- Still faces size limits
- File system is simpler

## Core Design Principles

1. **Uniform Tool Interface**: Everything exposed as MCP tools, whether simple function or complex multi-agent workflow
2. **Auto-Discovery**: Tools are automatically discovered via `@tool` decorator - no manual registration
3. **Composability**: Simple tools can be composed by agents; agent tools handle complex workflows
4. **Separation of Concerns**: Domain logic (`codes/`) separate from tool wrappers (`tools/`, `agent_tools/`)
5. **Stateless Execution**: Each tool call is independent; state managed through file I/O

## References

- **MCP Specification**: https://modelcontextprotocol.io/
- **Smolagents**: https://github.com/huggingface/smolagents
- **CLASS**: https://github.com/lesgourg/class_public
- **eBOSS DR14**: https://data.sdss.org/sas/dr14/eboss/lss/
