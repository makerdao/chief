// SPDX-License-Identifier: GPL-3.0-or-later

// DssChief.t.sol - tests for DssChief.sol

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

import "../src/DssChief.sol";
import "./mocks/TokenMock.sol";

contract DssChiefTest is Test {
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
    uint256 constant initialBalance = 1000000 ether;
    uint256 constant uLargeInitialBalance = initialBalance / 3;
    uint256 constant uMediumInitialBalance = initialBalance / 4;
    uint256 constant uSmallInitialBalance = initialBalance / 5;

    DssChief chief;
    TokenMock gov;

    // u prefix: user
    address uLarge;
    address uMedium;
    address uSmall;

    function setUp() public {
        gov = new TokenMock();
        gov.mint(address(this), initialBalance);

        chief = new DssChief(address(gov), electionSize, 80_000 ether);

        uLarge = address(123);
        uMedium = address(456);
        uSmall = address(789);

        assert(initialBalance > uLargeInitialBalance + uMediumInitialBalance +
               uSmallInitialBalance);
        assert(uLargeInitialBalance < uMediumInitialBalance + uSmallInitialBalance);

        gov.transfer(address(uLarge), uLargeInitialBalance);
        gov.transfer(address(uMedium), uMediumInitialBalance);
        gov.transfer(address(uSmall), uSmallInitialBalance);
        vm.roll(1); // Block number = 1
    }

    function _enableSystem() internal {
        address[] memory slate = new address[](1);
        slate[0] = address(0);
        gov.approve(address(chief), 80_000 ether);
        chief.lock(80000 ether);
        chief.vote(slate);
        chief.launch();
    }

    function _initialVote() internal returns (bytes32 slateID) {
        uint uMediumLockedAmt = uMediumInitialBalance;
        vm.startPrank(uMedium);
        gov.approve(address(chief), uMediumLockedAmt);
        chief.lock(uMediumLockedAmt);

        address[] memory uMediumSlate = new address[](3);
        uMediumSlate[0] = c1;
        uMediumSlate[1] = c2;
        uMediumSlate[2] = c3;
        slateID = chief.vote(uMediumSlate);

        // Lift the chief.
        chief.lift(c1);
        vm.stopPrank();
    }

    function testLaunchThreshold() public {
        assertEq(chief.live(), 0);
        address[] memory slate = new address[](1);
        slate[0] = address(0);
        gov.approve(address(chief), 80_000 ether);
        chief.lock(80000 ether - 1);
        chief.vote(slate);

        vm.expectRevert("DssChief/less-than-threshold");
        chief.launch();
        chief.lock(1);
        chief.launch();
        assertEq(chief.live(), 1);
    }

    function testLaunchHat() public {
        address[] memory slate = new address[](1);
        address    zero_address = address(0);
        address nonzero_address = address(1);
        slate[0] = nonzero_address;
        gov.approve(address(chief), 80000 ether);
        chief.lock(80000 ether);
        chief.vote(slate);
        chief.lift(nonzero_address);
        assertEq(chief.hat(), nonzero_address);
        assertTrue(!chief.canCall(nonzero_address, address(0), 0x00000000));

        vm.expectRevert("DssChief/not-address-zero");
        chief.launch();
        slate[0] = zero_address;
        chief.vote(slate);
        chief.lift(zero_address);
        assertEq(chief.hat(), zero_address);
        assertTrue(!chief.canCall(zero_address, address(0), 0x00000000));
        chief.launch();
        assertTrue(chief.canCall(zero_address, address(0), 0x00000000));
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

    function testEtchRequiresOrderedSets() public {
        address[] memory candidates = new address[](3);
        candidates[0] = c2;
        candidates[1] = c1;
        candidates[2] = c3;

        vm.expectRevert("DssChief/yays-not-ordered");
        vm.prank(uSmall);
        chief.etch(candidates);
    }

    function testLockDebitsUser() public {
        assertTrue(gov.balanceOf(address(uLarge)) == uLargeInitialBalance);

        uint lockedAmt = uLargeInitialBalance / 10;
        vm.startPrank(uLarge);
        gov.approve(address(chief), lockedAmt);
        chief.lock(lockedAmt);

        assertTrue(gov.balanceOf(address(uLarge)) == uLargeInitialBalance - lockedAmt);
    }

    function testFreeAfterLock() public {
        uint uLargeLockedAmt = uLargeInitialBalance / 2;
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);
        vm.roll(2);
        chief.free(uLargeLockedAmt);
    }

    function testFreeAfterLockSameBlock() public {
        uint uLargeLockedAmt = uLargeInitialBalance / 2;
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);
        vm.expectRevert("DssChief/cant-free-same-block");
        chief.free(uLargeLockedAmt);
    }

    function testChangingWeightAfterVoting() public {
        uint uLargeLockedAmt = uLargeInitialBalance / 2;
        vm.startPrank(uLarge);
        gov.approve(address(chief), uLargeLockedAmt);
        chief.lock(uLargeLockedAmt);

        address[] memory uLargeSlate = new address[](1);
        uLargeSlate[0] = c1;
        chief.vote(uLargeSlate);

        assertTrue(chief.approvals(c1) == uLargeLockedAmt);

        // Changing weight should update the weight of our candidate.
        vm.roll(2);
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
        vm.roll(2);
        chief.free(uMediumInitialBalance);

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
        vm.expectRevert("DssChief/not-higher-current-hat");
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
        chief.lift(c4);

        // Now restore the old order using a slate ID.
        vm.startPrank(uSmall);
        gov.approve(address(chief), uSmallInitialBalance);
        chief.lock(uSmallInitialBalance);
        chief.vote(slateID);

        // Update the elected set to reflect the restored order.
        chief.lift(c1);
    }

    function testVoteSlateEmptyAndNotEtched() public {
        address[] memory emptySlate = new address[](0);
        chief.vote(emptySlate);

        vm.expectRevert("DssChief/invalid-slate");
        chief.vote(bytes32(0x1010101010101010101010101010101010101010101010101010101010101010));
    }

    function testChiefOwner() public {
        assertEq(chief.owner(), address(0));
    }

    function testChiefAuthority() public {
        assertEq(chief.authority(), address(chief));
    }
}
