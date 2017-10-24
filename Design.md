# Introduction

The contracts in this repository form the basis of our ICO framework. This document describes the way they interact and the projected paths for extensibility.

# Overview

There are two main components in this ICO framework: the crowdsale contract and the token contract. In a typical deployment the crowdsale contract is only active for the duration of the ICO and the token contract is active for the remainder of the lifetime of the blockchain. The crowdsale contract is [`Crowdsale`](contracts/Crowdsale.sol) and the token contract is [`CrowdsaleToken`](contracts/CrowdsaleToken.sol). However, the majority of the functionality they provide is implemented in other contracts they inherit from.

The `Crowdsale` contract inherits from the [`GenericCrowdsale`](contracts/GenericCrowdsale.sol) contract which implements basic investing and configuration functions in addition to a state machine to restrict calls to some of those functions.

The `CrowdsaleToken` contract is a bit more complex: it inherits from the [`ReleasableToken`](contracts/ReleasableToken.sol) contract and the [`MintableToken`](contracts/MintableToken.sol) contract. Those two are the core token contracts that offer basic functionality for the token in compliance with the ERC20 standard. Additionally, it inherits from [`UpgradeableToken`](contracts/UpgradeableToken.sol) which provides an upgrade mechanism and [`LostAndFoundToken`](contracts/LostAndFoundToken.sol) that provides a safeguard against ERC20 tokens getting stuck in the contract.

There are two contracts that require configuration according to the characteristics desired of the ICO. The first one is the `Crowdsale` and the second one is the `CrowdsaleToken`. In the former it is necessary to customize the constructor and implement three functions while in the latter it is necessary to set the name and symbol of the token.

# Design

## `GenericCrowdsale`

The generic crowdsale contract handles the general investment logic and time intervals during which they can happen. Through inversion of control a child contract can customize the way the crowdsale behaves. There are three functions that require implementation for it to be complete: `calculateTokenAmount`, `assignTokens` and `isCrowdsaleFull`. The first one must be implemented to provide a pricing scheme for the ICO. The second one must implement the assignation of tokens through the crowdsale. Finally, the third one must implement the criterion according to which the crowdsale can be considered successful before the ending block is reached. Apart from these there is one more internal function that can be overriden if desired: the `returnExcedent` function. This function is meant to refund excess weis that couldn't contribute to the ICO according to the pricing scheme implemented in `calculateTokenAmount`. The default implementation transfers back the excess weis but a more sophisticated refund mechanism may be desired instead (e.g. through withdrawal from the contract).

## `CrowdsaleToken`

This contract inherits most of its functionality from several other contracts. An important objective when writing token contracts that we had in mind is encapsulating all the functionality we could. This allows easy extension of different implementations of the ERC20 standard token. For example, we wrote the [`Burnable`](contracts/Burnable.sol) internal interface. Its sole purpose is offering a function signature that eliminates tokens. We use this interface in the `UpgradeableToken` contract extension. The `CrowdsaleToken` contract itself only provides a constructor and some overrides. `MintableToken` offers a minting extension in the same fashion assuming the token contract implements [`Mintable`](contracts/Mintable.sol).