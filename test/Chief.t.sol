// SPDX-License-Identifier: GPL-3.0-or-later

// Chief.t.sol - tests for Chief.sol

// Copyright (C) 2017 DappHub, LLC
// Copyright (C) 2023 Dai Foundation

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

pragma solidity ^0.8.16;

import "forge-std/Test.sol";

import "../src/Chief.sol";
import "./mocks/TokenMock.sol";

contract ChiefTest is Test {
    uint256 constant electionSize = 3;

    // c prefix: candidate
    address constant c1 = address(0x1);
    address constant c2 = address(0x2);
    address constant c3 = address(0x3);
    address constant c4 = address(0x4);
    address constant c5 = address(0x5);
    address constant c6 = address(0x6);
    address constant c7 = address(0x7);
    address constant c8 = address(0x8);
    address constant c9 = address(0x9);
    uint256 constant initialBalance = 1_000_000 ether;
    uint256 constant uLargeInitialBalance = initialBalance / 3;
    uint256 constant uMediumInitialBalance = initialBalance / 4;
    uint256 constant uSmallInitialBalance = initialBalance / 5;

    Chief chief;
    TokenMock gov;

    // u prefix: user
    address uLarge;
    address uMedium;
    address uSmall;

    event Launch();
    event Lock(uint256 wad);
    event Free(uint256 wad);
    event Etch(bytes32 indexed slate, address[] yays);
    event Vote(bytes32 indexed slate);
    event Hold(address indexed whom);
    event Lift(address indexed whom);

    function setUp() public {
        gov = new TokenMock();
        gov.mint(address(this), initialBalance);

        chief = new Chief(address(gov), electionSize, 80_000 ether);

        uLarge = address(123);
        uMedium = address(456);
        uSmall = address(789);

        assert(initialBalance > uLargeInitialBalance + uMediumInitialBalance +
               uSmallInitialBalance);
        assert(uLargeInitialBalance < uMediumInitialBalance + uSmallInitialBalance);

        gov.transfer(address(uLarge), uLargeInitialBalance);
        gov.transfer(address(uMedium), uMediumInitialBalance);
        gov.transfer(address(uSmall), uSmallInitialBalance);
        vm.roll(1_000); // Block number = 1000
    }

    function _enableSystem() internal {
        address[] memory yays = new address[](1);
        yays[0] = address(0);
        gov.approve(address(chief), 80_000 ether);
        vm.expectEmit();
        emit Lock(80_000 ether);
        chief.lock(80_000 ether);
        bytes32 slate = keccak256(abi.encodePacked(yays));
        emit Etch(slate, yays);
        vm.expectEmit();
        emit Vote(slate);
        chief.vote(yays);

        vm.roll(block.number + 1);
        vm.expectEmit();
        emit Launch();
        chief.launch();
    }

    function _initialVote() internal returns (bytes32 slateID) {
        uint256 uMediumLockedAmt = uMediumInitialBalance;
        vm.startPrank(uMedium);
        gov.approve(address(chief), uMediumLockedAmt);
        chief.lock(uMediumLockedAmt);

        address[] memory uMediumSlate = new address[](3);
        uMediumSlate[0] = c1;
        uMediumSlate[1] = c2;
        uMediumSlate[2] = c3;
        slateID = chief.vote(uMediumSlate);

        // Lift the chief
        vm.roll(block.number + 1);
        chief.lift(c1);
        vm.stopPrank();
    }

    function testLaunchAlreadyLive() public {
        assertEq(chief.live(), 0);
        address[] memory slate = new address[](1);
        slate[0] = address(0);
        gov.approve(address(chief), 80_000 ether);
        chief.lock(80000 ether);
        chief.vote(slate);
        vm.roll(block.number + 1);
        chief.launch();
        assertEq(chief.live(), 1);

        vm.expectRevert("Chief/already-live");
        chief.launch();
    }

    function testLaunchHatNotZero() public {
        address[] memory slate = new address[](1);
        address    zero_address = address(0);
        address nonzero_address = address(1);
        slate[0] = nonzero_address;
        gov.approve(address(chief), 80000 ether);
        chief.lock(80000 ether);
        chief.vote(slate);
        vm.roll(block.number + 1);
        chief.lift(nonzero_address);
        assertEq(chief.hat(), nonzero_address);
        assertTrue(!chief.canCall(nonzero_address, address(0), 0x00000000));

        vm.expectRevert("Chief/not-address-zero");
        chief.launch();
        slate[0] = zero_address;
        chief.vote(slate);
        vm.roll(block.number + 1);
        chief.lift(zero_address);
        assertEq(chief.hat(), zero_address);
        assertTrue(!chief.canCall(zero_address, address(0), 0x00000000));
        chief.launch();
        assertTrue(chief.canCall(zero_address, address(0), 0x00000000));
    }

    function testLaunchBelowThreshold() public {
        assertEq(chief.live(), 0);
        address[] memory slate = new address[](1);
        slate[0] = address(0);
        gov.approve(address(chief), 80_000 ether);
        chief.lock(80000 ether - 1);
        chief.vote(slate);

        vm.expectRevert("Chief/less-than-threshold");
        chief.launch();
        chief.lock(1);
        vm.roll(block.number + 1);
        chief.launch();
        assertEq(chief.live(), 1);
    }

    function testLaunchLockInSameBlock() public {
        assertEq(chief.live(), 0);
        address[] memory slate = new address[](1);
        slate[0] = address(0);
        gov.approve(address(chief), 80_000 ether);
        chief.lock(80000 ether);
        chief.vote(slate);

        vm.expectRevert("Chief/cant-launch-same-block");
        chief.launch();
        vm.roll(block.number + 1);
        chief.launch();
        assertEq(chief.live(), 1);
    }

    function testEtchReturnsSameIdForSameSets() public {
        address[] memory candidates = new address[](3);
        candidates[0] = c1;
        candidates[1] = c2;
        candidates[2] = c3;

        vm.prank(uSmall);
        bytes32 id = chief.etch(candidates);
        assertTrue(id != 0x0);
        vm.prank(uMedium);
        assertEq32(id, chief.etch(candidates));
    }

    function testSizeZeroSlate() public {
        address[] memory candidates = new address[](0);
        vm.startPrank(uSmall);
        bytes32 id = chief.etch(candidates);
        chief.vote(id);
    }

    function testSizeOneSlate() public {
        address[] memory candidates = new address[](1);
        candidates[0] = c1;
        vm.startPrank(uSmall);
        bytes32 id = chief.etch(candidates);
        chief.vote(id);
    }

    function testEtchRequiresLessThanMaxYays() public {
        address[] memory candidates = new address[](4);
        candidates[0] = c2;
        candidates[1] = c1;
        candidates[2] = c3;
        candidates[3] = address(0xFFF);

        vm.expectRevert("Chief/greater-max-yays");
        vm.prank(uSmall);
        chief.etch(candidates);
    }

    function testEtchRequiresOrderedSets() public {
        address[] memory candidates = new address[](3);
        candidates[0] = c2;
        candidates[1] = c1;
        candidates[2] = c3;

        vm.expectRevert("Chief/yays-not-ordered");
        vm.prank(uSmall);
        chief.etch(candidates);
    }

    function testLockDebitsUser() public {
        assertTrue(gov.balanceOf(address(uLarge)) == uLargeInitialBalance);

        uint256 lockedAmt = uLargeInitialBalance / 10;
        vm.startPrank(uLarge);
        gov.approve(address(chief), lockedAmt);
        chief.lock(lockedAmt);

        assertTrue(gov.balanceOf(address(uLarge)) == uLargeInitialBalance - lockedAmt);
    }

    function testLiftAfterLock() public {
        uint256 uLargeLockedAmt = uLargeInitialBalance / 2;
        vm.startPrank(uLarge);
        address[] memory candidates = new address[](1);
        candidates[0] = c1;
        chief.vote(candidates);
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);
        vm.roll(block.number + 1);
        chief.lift(c1);
    }

    function testLiftAfterLockSameBlock() public {
        uint256 uLargeLockedAmt = uLargeInitialBalance / 2;
        vm.startPrank(uLarge);
        address[] memory candidates = new address[](1);
        candidates[0] = c1;
        chief.vote(candidates);
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);
        vm.expectRevert("Chief/cant-lift-same-block");
        chief.lift(c1);
    }

    function testChangingWeightAfterVoting() public {
        uint256 uLargeLockedAmt = uLargeInitialBalance / 2;
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);

        address[] memory uLargeSlate = new address[](1);
        uLargeSlate[0] = c1;
        chief.vote(uLargeSlate);

        assertTrue(chief.approvals(c1) == uLargeLockedAmt);

        // Changing weight should update the weight of our candidate.
        vm.expectEmit();
        emit Free(uLargeLockedAmt);
        chief.free(uLargeLockedAmt);
        assertTrue(chief.approvals(c1) == 0);

        uLargeLockedAmt = uLargeInitialBalance / 4;
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);

        assertTrue(chief.approvals(c1) == uLargeLockedAmt);
    }

    function testVotingAndReordering() public {
        assertTrue(gov.balanceOf(address(uLarge)) == uLargeInitialBalance);

        _initialVote();

        // Upset the order.
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeInitialBalance);
        chief.lock(uLargeInitialBalance);

        address[] memory uLargeSlate = new address[](1);
        uLargeSlate[0] = c3;
        chief.vote(uLargeSlate);
    }

    function testAuthEnabledSystem() public {
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeInitialBalance);
        chief.lock(uLargeInitialBalance);

        address[] memory uLargeSlate = new address[](1);
        uLargeSlate[0] = c1;
        chief.vote(uLargeSlate);
        vm.stopPrank();

        _enableSystem();

        vm.roll(block.number + 1);
        vm.expectEmit();
        emit Lift(c1);
        chief.lift(c1);
        assertTrue(chief.canCall(c1, address(0), 0x00000000));
    }

    function testAuthNotEnabledSystem() public {
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeInitialBalance);
        chief.lock(uLargeInitialBalance);

        address[] memory uLargeSlate = new address[](1);
        uLargeSlate[0] = c1;
        chief.vote(uLargeSlate);

        vm.roll(block.number + 1);
        chief.lift(c1);
        assertTrue(!chief.canCall(c1, address(0), 0x00000000));
    }

    function testLiftHalfApprovals() public {
        _enableSystem();
        _initialVote();

        // Upset the order.
        vm.startPrank(uSmall);
        gov.approve(address(chief), uSmallInitialBalance);
        chief.lock(uSmallInitialBalance);

        address[] memory uSmallSlate = new address[](1);
        uSmallSlate[0] = c3;
        chief.vote(uSmallSlate);

        vm.stopPrank();
        vm.startPrank(uMedium);
        chief.free(uMediumInitialBalance);

        vm.roll(block.number + 1);
        chief.lift(c3);

        assertTrue(!chief.canCall(c1, address(0), 0x00000000));
        assertTrue(!chief.canCall(c2, address(0), 0x00000000));
        assertTrue(chief.canCall(c3, address(0), 0x00000000));
    }

    function testVotingAndReorderingWithoutWeight() public {
        assertEq(gov.balanceOf(address(uLarge)), uLargeInitialBalance);

        _initialVote();

        // Vote without weight.
        address[] memory uLargeSlate = new address[](1);
        uLargeSlate[0] = c3;
        vm.prank(uLarge);
        chief.vote(uLargeSlate);

        // Attempt to update the elected set.
        vm.expectRevert("Chief/not-higher-current-hat");
        chief.lift(c3);
    }

    function testVotingBySlateId() public {
        assertEq(gov.balanceOf(address(uLarge)), uLargeInitialBalance);

        bytes32 slateID = _initialVote();

        // Upset the order.
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeInitialBalance);
        chief.lock(uLargeInitialBalance);

        address[] memory uLargeSlate = new address[](1);
        uLargeSlate[0] = c4;
        chief.vote(uLargeSlate);
        vm.stopPrank();

        // Update the elected set to reflect the new order.
        vm.roll(block.number + 1);
        chief.lift(c4);

        // Now restore the old order using a slate ID.
        vm.startPrank(uSmall);
        gov.approve(address(chief), uSmallInitialBalance);
        chief.lock(uSmallInitialBalance);
        chief.vote(slateID);

        // Update the elected set to reflect the restored order.
        vm.roll(block.number + 1);
        chief.lift(c1);
    }

    function testVoteSlateEmptyAndNotEtched() public {
        address[] memory emptySlate = new address[](0);
        chief.vote(emptySlate);

        vm.expectRevert("Chief/invalid-slate");
        chief.vote(bytes32(0x1010101010101010101010101010101010101010101010101010101010101010));
    }

    function testHoldForLaunching() public {
        assertEq(chief.approvals(address(0)), chief.approvals(chief.hat()));
        assertEq(chief.holdTrigger(), 0);
        chief.hold(address(0));
        assertEq(chief.holdTrigger(), block.number);
    }

    function testHoldForLifting() public {
        _enableSystem();
        vm.prank(uLarge); gov.approve(address(chief), type(uint256).max);

        assertEq(gov.balanceOf(address(uLarge)), uLargeInitialBalance);
        assertEq(chief.holdTrigger(), 0);

        vm.prank(uLarge); chief.lock(80_001 ether);        // can lock

        vm.expectRevert("Chief/no-reason-to-hold");
        chief.hold(c1);

        address[] memory uLargeSlate = new address[](1);
        uLargeSlate[0] = c1;
        vm.prank(uLarge); chief.vote(uLargeSlate);

        vm.expectEmit();
        emit Hold(c1);
        chief.hold(c1);                                    // can hold
        assertEq(chief.holdTrigger(), block.number);
        vm.prank(uLarge); chief.lock(10 ether);            // can still lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold again
        chief.hold(c1);

        // move to first block of the hold
        vm.roll(block.number + 1);

        vm.expectRevert("Chief/no-lock-during-hold");
        vm.prank(uLarge); chief.lock(10 ether);            // can not lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);

        // move to last block of the hold
        vm.roll(block.number + 4);

        vm.expectRevert("Chief/no-lock-during-hold");
        vm.prank(uLarge); chief.lock(10 ether);            // can not lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);

        // move to first block of the cooldown
        vm.roll(block.number + 1);

        vm.prank(uLarge); chief.lock(10 ether);            // can lock again
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);

        // move to last block of the cooldown
        vm.roll(block.number + 18);

        vm.prank(uLarge); chief.lock(10 ether);            // can still lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);

        // move to first block after the cooldown
        vm.roll(block.number + 1);

        vm.prank(uLarge); chief.lock(10 ether);            // can lock
        chief.hold(c1);                                    // can hold again
        assertEq(chief.holdTrigger(), block.number);
        vm.prank(uLarge); chief.lock(10 ether);            // can still lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold again
        chief.hold(c1);

        // move to first block of the new hold
        vm.roll(block.number + 1);

        vm.expectRevert("Chief/no-lock-during-hold");
        vm.prank(uLarge); chief.lock(10 ether);            // can not lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);
    }

    function testChiefOwner() public {
        assertEq(chief.owner(), address(0));
    }

    function testChiefAuthority() public {
        assertEq(chief.authority(), address(chief));
    }
}
