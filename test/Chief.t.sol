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

pragma solidity ^0.8.21;

import "forge-std/Test.sol";

import "src/Chief.sol";
import "test/mocks/TokenMock.sol";

contract ChiefTest is Test {
    uint256 constant electionSize = 3;

    // c prefix: candidate
    address constant c1 = address(0x1);
    address constant c2 = address(0x2);
    address constant c3 = address(0x3);
    address constant c4 = address(0x4);
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
        deal(address(gov), address(this), initialBalance);

        chief = new Chief(address(gov), electionSize, 80_000 ether);

        uLarge = address(123);
        uMedium = address(456);
        uSmall = address(789);

        assertGt(initialBalance, uLargeInitialBalance + uMediumInitialBalance + uSmallInitialBalance);
        assertLt(uLargeInitialBalance, uMediumInitialBalance + uSmallInitialBalance);

        gov.transfer(uLarge, uLargeInitialBalance);
        gov.transfer(uMedium, uMediumInitialBalance);
        gov.transfer(uSmall, uSmallInitialBalance);
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

    function _initialVote() internal returns (bytes32 slate) {
        vm.startPrank(uMedium);
        gov.approve(address(chief), uMediumInitialBalance);
        chief.lock(uMediumInitialBalance);

        address[] memory uMediumYays = new address[](3);
        uMediumYays[0] = c1;
        uMediumYays[1] = c2;
        uMediumYays[2] = c3;
        slate = chief.vote(uMediumYays);
        vm.stopPrank();

        // Lift the new hat
        vm.roll(block.number + 1);
        chief.lift(c1);
    }

    function testCompatibilityGetters() public view {
        assertEq(address(chief.GOV()), address(chief.gov()));
        assertEq(chief.MAX_YAYS(), chief.maxYays());
    }

    function testSlateLengthGetter() public {
        address[] memory yays0 = new address[](0);
        address[] memory yays1 = new address[](1);
        yays1[0] = address(1);
        address[] memory yays2 = new address[](2);
        yays2[0] = address(1);
        yays2[1] = address(2);
        address[] memory yays3 = new address[](3);
        yays3[0] = address(1);
        yays3[1] = address(2);
        yays3[2] = address(3);
        bytes32 slate0 = chief.etch(yays0);
        bytes32 slate1 = chief.etch(yays1);
        bytes32 slate2 = chief.etch(yays2);
        bytes32 slate3 = chief.etch(yays3);
        assertEq(chief.length(slate0), 0);
        assertEq(chief.length(slate1), 1);
        assertEq(chief.length(slate2), 2);
        assertEq(chief.length(slate3), 3);
    }

    function testLaunchAlreadyLive() public {
        assertEq(chief.live(), 0);
        _enableSystem();
        assertEq(chief.live(), 1);

        vm.expectRevert("Chief/already-live");
        chief.launch();
    }

    function testLaunchHatNotZero() public {
        address[] memory yays = new address[](1);
        yays[0] = address(1);
        gov.approve(address(chief), 80_000 ether);
        chief.lock(80_000 ether);
        chief.vote(yays);
        vm.roll(block.number + 1);
        chief.lift(address(1));
        assertEq(chief.hat(), address(1));
        assertFalse(chief.canCall(address(1), address(0), bytes4(0)));

        vm.expectRevert("Chief/not-address-zero");
        chief.launch();
        yays[0] = address(0);
        chief.vote(yays);
        vm.roll(block.number + 1);
        chief.lift(address(0));
        assertEq(chief.hat(), address(0));
        assertEq(chief.live(), 0);
        assertFalse(chief.canCall(address(0), address(0), bytes4(0)));
        chief.launch();
        assertEq(chief.live(), 1);
        assertTrue(chief.canCall(address(0), address(0), bytes4(0)));
    }

    function testLaunchBelowThreshold() public {
        address[] memory yays = new address[](1);
        yays[0] = address(0);
        gov.approve(address(chief), 80_000 ether);
        chief.lock(80_000 ether - 1);
        chief.vote(yays);

        vm.expectRevert("Chief/less-than-threshold");
        chief.launch();
        chief.lock(1);
        vm.roll(block.number + 1);
        assertEq(chief.hat(), address(0));
        assertEq(chief.live(), 0);
        assertFalse(chief.canCall(address(0), address(0), bytes4(0)));
        chief.launch();
        assertEq(chief.live(), 1);
        assertTrue(chief.canCall(address(0), address(0), bytes4(0)));
    }

    function testLaunchLockInSameBlock() public {
        assertEq(chief.live(), 0);
        address[] memory yays = new address[](1);
        yays[0] = address(0);
        gov.approve(address(chief), 80_000 ether);
        chief.lock(80_000 ether);
        chief.vote(yays);

        vm.expectRevert("Chief/cant-launch-same-block");
        chief.launch();
        vm.roll(block.number + 1);
        chief.launch();
        assertEq(chief.live(), 1);
    }

    function testEtchReturnsSameSlateForSameYays() public {
        address[] memory yays = new address[](3);
        yays[0] = c1;
        yays[1] = c2;
        yays[2] = c3;

        vm.prank(uSmall);
        bytes32 slate = chief.etch(yays);
        assertNotEq(slate, bytes32(0));
        vm.prank(uMedium);
        assertEq32(chief.etch(yays), slate);
    }

    function testSizeZeroSlate() public {
        address[] memory yays = new address[](0);
        vm.startPrank(uSmall);
        bytes32 slate = chief.etch(yays);
        chief.vote(slate);
        vm.stopPrank();
    }

    function testSizeOneSlate() public {
        address[] memory yays = new address[](1);
        yays[0] = c1;
        vm.startPrank(uSmall);
        bytes32 slate = chief.etch(yays);
        chief.vote(slate);
        vm.stopPrank();
    }

    function testEtchRequiresLessThanMaxYays() public {
        address[] memory yays = new address[](4);
        yays[0] = c2;
        yays[1] = c1;
        yays[2] = c3;
        yays[3] = address(0xFFF);

        vm.expectRevert("Chief/greater-max-yays");
        vm.prank(uSmall);
        chief.etch(yays);
    }

    function testEtchRequiresOrderedSets() public {
        address[] memory yays = new address[](3);
        yays[0] = c2;
        yays[1] = c1;
        yays[2] = c3;

        vm.expectRevert("Chief/yays-not-ordered");
        vm.prank(uSmall);
        chief.etch(yays);
    }

    function testLockFree() public {
        assertEq(gov.balanceOf(uLarge), uLargeInitialBalance);
        uint256 lockedAmt = uLargeInitialBalance / 10;
        vm.startPrank(uLarge);
        gov.approve(address(chief), 2 * lockedAmt);
        chief.lock(lockedAmt);
        assertEq(gov.balanceOf(uLarge), uLargeInitialBalance - lockedAmt);
        assertEq(chief.deposits(uLarge), lockedAmt);
        chief.lock(lockedAmt);
        assertEq(gov.balanceOf(uLarge), uLargeInitialBalance - 2 * lockedAmt);
        assertEq(chief.deposits(uLarge), 2 * lockedAmt);
        chief.free(lockedAmt);
        assertEq(gov.balanceOf(uLarge), uLargeInitialBalance - lockedAmt);
        assertEq(chief.deposits(uLarge), lockedAmt);
        vm.stopPrank();
    }

    function testLiftAfterLock() public {
        uint256 uLargeLockedAmt = uLargeInitialBalance / 2;
        vm.startPrank(uLarge);
        address[] memory yays = new address[](1);
        yays[0] = c1;
        chief.vote(yays);
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);
        vm.stopPrank();
        vm.expectRevert("Chief/cant-lift-same-block");
        chief.lift(c1);
        vm.roll(block.number + 1);
        chief.lift(c1);
    }

    function testChangingWeightAfterVoting() public {
        uint256 uLargeLockedAmt = uLargeInitialBalance / 2;
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);

        address[] memory uLargeYays = new address[](1);
        uLargeYays[0] = c1;
        chief.vote(uLargeYays);

        assertEq(chief.approvals(c1), uLargeLockedAmt);

        // Changing weight should update the weight of our candidate.
        vm.expectEmit();
        emit Free(uLargeLockedAmt);
        chief.free(uLargeLockedAmt);
        assertEq(chief.approvals(c1), 0);

        uLargeLockedAmt = uLargeInitialBalance / 4;
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);
        vm.stopPrank();

        assertEq(chief.approvals(c1), uLargeLockedAmt);
    }

    function testVotingAndReordering() public {
        assertEq(gov.balanceOf(uLarge), uLargeInitialBalance);

        _initialVote();

        // Upset the order.
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeInitialBalance);
        chief.lock(uLargeInitialBalance);

        address[] memory uLargeYays = new address[](1);
        uLargeYays[0] = c3;
        chief.vote(uLargeYays);
        vm.stopPrank();
    }

    function testAuthEnabledSystem() public {
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeInitialBalance);
        chief.lock(uLargeInitialBalance);

        address[] memory uLargeYays = new address[](1);
        uLargeYays[0] = c1;
        chief.vote(uLargeYays);
        vm.stopPrank();

        _enableSystem();

        vm.roll(block.number + 1);
        vm.expectEmit();
        emit Lift(c1);
        chief.lift(c1);
        assertTrue(chief.canCall(c1, address(0), bytes4(0)));
    }

    function testAuthNotEnabledSystem() public {
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeInitialBalance);
        chief.lock(uLargeInitialBalance);

        address[] memory uLargeYays = new address[](1);
        uLargeYays[0] = c1;
        chief.vote(uLargeYays);
        vm.stopPrank();

        vm.roll(block.number + 1);
        chief.lift(c1);
        assertFalse(chief.canCall(c1, address(0), bytes4(0)));
    }

    function testLiftHalfApprovals() public {
        _enableSystem();
        _initialVote();

        // Upset the order.
        vm.startPrank(uSmall);
        gov.approve(address(chief), uSmallInitialBalance);
        chief.lock(uSmallInitialBalance);

        address[] memory uSmallYays = new address[](1);
        uSmallYays[0] = c3;
        chief.vote(uSmallYays);

        vm.stopPrank();
        vm.startPrank(uMedium);
        chief.free(uMediumInitialBalance);
        vm.stopPrank();

        vm.roll(block.number + 1);
        chief.lift(c3);

        assertFalse(chief.canCall(c1, address(0), bytes4(0)));
        assertFalse(chief.canCall(c2, address(0), bytes4(0)));
        assertTrue(chief.canCall(c3, address(0), bytes4(0)));
    }

    function testVotingAndReorderingWithoutWeight() public {
        assertEq(gov.balanceOf(uLarge), uLargeInitialBalance);

        _initialVote();

        // Vote without weight.
        address[] memory uLargeYays = new address[](1);
        uLargeYays[0] = c3;
        vm.prank(uLarge);
        chief.vote(uLargeYays);

        // Attempt to update the elected set.
        vm.expectRevert("Chief/not-higher-current-hat");
        chief.lift(c3);
    }

    function testVotingBySlate() public {
        assertEq(gov.balanceOf(uLarge), uLargeInitialBalance);

        bytes32 slate = _initialVote();

        // Upset the order.
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeInitialBalance);
        chief.lock(uLargeInitialBalance);

        address[] memory uLargeYays = new address[](1);
        uLargeYays[0] = c4;
        chief.vote(uLargeYays);
        vm.stopPrank();

        // Update the elected set to reflect the new order.
        vm.roll(block.number + 1);
        chief.lift(c4);

        // Now restore the old order using a slate.
        vm.startPrank(uSmall);
        gov.approve(address(chief), uSmallInitialBalance);
        chief.lock(uSmallInitialBalance);
        chief.vote(slate);
        vm.stopPrank();

        // Update the elected set to reflect the restored order.
        vm.roll(block.number + 1);
        chief.lift(c1);
    }

    function testVoteSlateEmptyAndNotEtched() public {
        address[] memory emptyYays = new address[](0);
        chief.vote(emptyYays);

        vm.expectRevert("Chief/invalid-slate");
        chief.vote(0x1010101010101010101010101010101010101010101010101010101010101010);
    }

    function testHoldForLaunching() public {
        assertEq(chief.approvals(address(0)), chief.approvals(chief.hat()));
        assertEq(chief.holdTrigger(), 0);
        assertEq(chief.hat(), address(0));
        vm.expectRevert("Chief/no-reason-to-hold");
        chief.hold(address(0));
        address[] memory yays = new address[](1);
        yays[0] = address(0);
        gov.approve(address(chief), 80_000 ether);
        chief.lock(80_000 ether - 1);
        chief.vote(yays);
        vm.expectRevert("Chief/no-reason-to-hold");
        chief.hold(address(0));
        chief.lock(1);
        vm.startPrank(uLarge);
        gov.approve(address(chief), type(uint256).max);
        chief.lock(80_000 ether + 1);
        yays[0] = address(1);
        chief.vote(yays);
        vm.roll(block.number + 1);
        chief.lift(address(1));
        assertEq(chief.hat(), address(1));
        assertEq(chief.approvals(address(0)), chief.launchThreshold());
        vm.expectRevert("Chief/no-reason-to-hold");
        chief.hold(address(0));
        chief.free(2);
        chief.lift(address(0));
        vm.stopPrank();
        assertEq(chief.hat(), address(0));
        chief.hold(address(0));
        assertEq(chief.holdTrigger(), block.number);
    }

    function testHoldForLifting() public {
        _enableSystem();
        vm.prank(uLarge); gov.approve(address(chief), type(uint256).max);

        assertEq(gov.balanceOf(uLarge), uLargeInitialBalance);
        assertEq(chief.holdTrigger(), 0);

        vm.prank(uLarge); chief.lock(80_001 ether);     // can lock

        vm.expectRevert("Chief/no-reason-to-hold");
        chief.hold(c1);

        address[] memory uLargeYays = new address[](1);
        uLargeYays[0] = c1;
        vm.prank(uLarge); chief.vote(uLargeYays);

        vm.expectEmit();
        emit Hold(c1);
        chief.hold(c1);                                 // can hold
        assertEq(chief.holdTrigger(), block.number);
        vm.prank(uLarge); chief.lock(10 ether);         // can still lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold again
        chief.hold(c1);

        // move to first block of the hold
        vm.roll(block.number + 1);

        vm.expectRevert("Chief/no-lock-during-hold");
        vm.prank(uLarge); chief.lock(10 ether);         // can not lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);

        // move to last block of the hold
        vm.roll(block.number + 4);

        vm.expectRevert("Chief/no-lock-during-hold");
        vm.prank(uLarge); chief.lock(10 ether);         // can not lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);

        // move to first block of the cooldown
        vm.roll(block.number + 1);

        vm.prank(uLarge); chief.lock(10 ether);         // can lock again
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);

        // move to last block of the cooldown
        vm.roll(block.number + 18);

        vm.prank(uLarge); chief.lock(10 ether);         // can still lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);

        // move to first block after the cooldown
        vm.roll(block.number + 1);

        vm.prank(uLarge); chief.lock(10 ether);         // can lock
        chief.hold(c1);                                 // can hold again
        assertEq(chief.holdTrigger(), block.number);
        vm.prank(uLarge); chief.lock(10 ether);         // can still lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold again
        chief.hold(c1);

        // move to first block of the new hold
        vm.roll(block.number + 1);

        vm.expectRevert("Chief/no-lock-during-hold");
        vm.prank(uLarge); chief.lock(10 ether);         // can not lock
        vm.expectRevert("Chief/cooldown-not-finished"); // can not hold
        chief.hold(c1);
    }

    function testOverflow() public {
        deal(address(gov), address(this), type(uint256).max);
        gov.approve(address(chief), type(uint256).max);
        chief.lock(type(uint256).max);
        deal(address(gov), address(this), type(uint256).max);
        gov.approve(address(chief), type(uint256).max);
        vm.expectRevert(stdError.arithmeticError);
        chief.lock(1);
    }
}
