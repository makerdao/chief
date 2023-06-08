// DssChief.spec

using TokenMock as gov;
using Auxiliar as aux;

methods {
    function live() external returns (uint256) envfree;
    function hat() external returns (address) envfree;
    function slates(bytes32, uint256) external returns (address) envfree;
    function votes(address) external returns (bytes32) envfree;
    function approvals(address) external returns (uint256) envfree;
    function deposits(address) external returns (uint256) envfree;
    function last(address) external returns (uint256) envfree;
    function gov() external returns (address) envfree;
    function maxYays() external returns (uint256) envfree;
    function launchThreshold() external returns (uint256) envfree;
    function length(bytes32) external returns (uint256) envfree;
    function gov.allowance(address, address) external returns (uint256) envfree;
    function gov.balanceOf(address) external returns (uint256) envfree;
    function aux.hashYays(address[]) external returns (bytes32) envfree;
}

// Verify correct storage changes for non reverting launch
rule launch() {
    env e;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    address hatBefore = hat();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    mathint approvalsBefore = approvals(anyAddr);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last(anyAddr);

    launch(e);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsAfter = approvals(anyAddr);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == 1, "launch did not set live to 1";
    assert hatAfter == hatBefore, "launch did not keep unchanged hat";
    assert slatesAfter == slatesBefore, "launch did not keep unchanged every slates[x][y]";
    assert votesAfter == votesBefore, "launch did not keep unchanged every votes[x]";
    assert approvalsAfter == approvalsBefore, "launch did not keep unchanged every approvals[x]";
    assert depositsAfter == depositsBefore, "launch did not keep unchanged every deposits[x]";
    assert lastAfter == lastBefore, "launch did not keep unchanged every last[x]";
}

// Verify revert rules on launch
rule launch_revert() {
    env e;

    mathint live = live();
    address hat = hat();
    address addr0 = 0;
    mathint approvals = approvals(addr0);
    mathint launchThreshold = launchThreshold();

    launch@withrevert(e);

    bool revert1 = e.msg.value > 0;
    bool revert2 = live != 0;
    bool revert3 = hat != addr0;
    bool revert4 = approvals < launchThreshold;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting lock
rule lock(uint256 wad) {
    env e;

    require maxYays() == 5;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    address otherAddr;
    require otherAddr != e.msg.sender;

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    bytes32 votesSender = votes(e.msg.sender);
    uint256 length = length(votesSender);
    require length <= maxYays();
    address addr0 = 0;
    address yaysSender0 = length >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address yaysSender1 = length >= 2 ? slates(votesSender, 1) : addr0;
    address yaysSender2 = length >= 3 ? slates(votesSender, 2) : addr0;
    address yaysSender3 = length >= 4 ? slates(votesSender, 3) : addr0;
    address yaysSender4 = length == 5 ? slates(votesSender, 4) : addr0;
    require length <= 1 || yaysSender1 > yaysSender0;
    require length <= 2 || yaysSender2 > yaysSender1;
    require length <= 3 || yaysSender3 > yaysSender2;
    require length <= 4 || yaysSender4 > yaysSender3;
    address yaysNotSender;
    require (length < 1 || yaysNotSender != yaysSender0) &&
            (length < 2 || yaysNotSender != yaysSender1) &&
            (length < 3 || yaysNotSender != yaysSender2) &&
            (length < 4 || yaysNotSender != yaysSender3) &&
            (length < 5 || yaysNotSender != yaysSender4);
    mathint approvalsYaysSender0Before = approvals(yaysSender0);
    mathint approvalsYaysSender1Before = approvals(yaysSender1);
    mathint approvalsYaysSender2Before = approvals(yaysSender2);
    mathint approvalsYaysSender3Before = approvals(yaysSender3);
    mathint approvalsYaysSender4Before = approvals(yaysSender4);
    mathint approvalsYaysNotSenderBefore = approvals(yaysNotSender);
    mathint depositsSenderBefore = deposits(e.msg.sender);
    mathint depositsOtherBefore = deposits(otherAddr);
    mathint lastOtherBefore = last(otherAddr);

    lock(e, wad);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsYaysSender0After = approvals(yaysSender0);
    mathint approvalsYaysSender1After = approvals(yaysSender1);
    mathint approvalsYaysSender2After = approvals(yaysSender2);
    mathint approvalsYaysSender3After = approvals(yaysSender3);
    mathint approvalsYaysSender4After = approvals(yaysSender4);
    mathint approvalsYaysNotSenderAfter = approvals(yaysNotSender);
    mathint depositsSenderAfter = deposits(e.msg.sender);
    mathint depositsOtherAfter = deposits(otherAddr);
    mathint lastSenderAfter = last(e.msg.sender);
    mathint lastOtherAfter = last(otherAddr);

    assert liveAfter == liveBefore, "lock did not keep unchanged live";
    assert hatAfter == hatBefore, "lock did not keep unchanged hat";
    assert slatesAfter == slatesBefore, "lock did not keep unchanged every slates[x][y]";
    assert votesAfter == votesBefore, "lock did not keep unchanged every votes[x]";
    assert length >= 1 => approvalsYaysSender0After == approvalsYaysSender0Before + wad, "lock did not increase approvals[yaysSender0] by wad";
    assert length >= 2 => approvalsYaysSender1After == approvalsYaysSender1Before + wad, "lock did not increase approvals[yaysSender1] by wad";
    assert length >= 3 => approvalsYaysSender2After == approvalsYaysSender2Before + wad, "lock did not increase approvals[yaysSender2] by wad";
    assert length >= 4 => approvalsYaysSender3After == approvalsYaysSender3Before + wad, "lock did not increase approvals[yaysSender3] by wad";
    assert length == 5 => approvalsYaysSender4After == approvalsYaysSender4Before + wad, "lock did not increase approvals[yaysSender4] by wad";
    assert approvalsYaysNotSenderAfter == approvalsYaysNotSenderBefore, "lock did not keep unchanged the rest of approvals[x]";
    assert depositsSenderAfter == depositsSenderBefore + wad, "lock did not increase deposits[sender] by wad";
    assert depositsOtherAfter == depositsOtherBefore, "lock did not keep unchanged the rest of deposits[x]";
    assert lastSenderAfter == to_mathint(e.block.number), "lock did not set last[sender] to block.number";
    assert lastOtherAfter == lastOtherBefore, "lock did not keep unchanged the rest of last[x]";
}

// Verify revert rules on lock
rule lock_revert(uint256 wad) {
    env e;

    require maxYays() == 5;
    require gov.balanceOf(e.msg.sender) >= wad;
    require gov.allowance(e.msg.sender, currentContract) >= wad;

    mathint depositsSender = deposits(e.msg.sender);
    bytes32 votesSender = votes(e.msg.sender);
    uint256 length = length(votesSender);
    require length <= maxYays();
    address addr0 = 0;
    address yaysSender0 = length >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address yaysSender1 = length >= 2 ? slates(votesSender, 1) : addr0;
    address yaysSender2 = length >= 3 ? slates(votesSender, 2) : addr0;
    address yaysSender3 = length >= 4 ? slates(votesSender, 3) : addr0;
    address yaysSender4 = length == 5 ? slates(votesSender, 4) : addr0;
    require length <= 1 || yaysSender1 > yaysSender0;
    require length <= 2 || yaysSender2 > yaysSender1;
    require length <= 3 || yaysSender3 > yaysSender2;
    require length <= 4 || yaysSender4 > yaysSender3;
    mathint app0 = approvals(yaysSender0);
    mathint app1 = approvals(yaysSender1);
    mathint app2 = approvals(yaysSender2);
    mathint app3 = approvals(yaysSender3);
    mathint app4 = approvals(yaysSender4);

    lock@withrevert(e, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = depositsSender + wad > max_uint256;
    bool revert3 = length >= 1 && app0 + wad > max_uint256;
    bool revert4 = length >= 2 && app1 + wad > max_uint256;
    bool revert5 = length >= 3 && app2 + wad > max_uint256;
    bool revert6 = length >= 4 && app3 + wad > max_uint256;
    bool revert7 = length == 5 && app4 + wad > max_uint256;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert revert6 => lastReverted, "revert6 failed";
    assert revert7 => lastReverted, "revert7 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5 || revert6 ||
                           revert7, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting free
rule free(uint256 wad) {
    env e;

    require maxYays() == 5;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    address otherAddr;
    require otherAddr != e.msg.sender;

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    bytes32 votesSender = votes(e.msg.sender);
    uint256 length = length(votesSender);
    require length <= maxYays();
    address addr0 = 0;
    address yaysSender0 = length >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address yaysSender1 = length >= 2 ? slates(votesSender, 1) : addr0;
    address yaysSender2 = length >= 3 ? slates(votesSender, 2) : addr0;
    address yaysSender3 = length >= 4 ? slates(votesSender, 3) : addr0;
    address yaysSender4 = length == 5 ? slates(votesSender, 4) : addr0;
    require length <= 1 || yaysSender1 > yaysSender0;
    require length <= 2 || yaysSender2 > yaysSender1;
    require length <= 3 || yaysSender3 > yaysSender2;
    require length <= 4 || yaysSender4 > yaysSender3;
    address yaysNotSender;
    require (length < 1 || yaysNotSender != yaysSender0) &&
            (length < 2 || yaysNotSender != yaysSender1) &&
            (length < 3 || yaysNotSender != yaysSender2) &&
            (length < 4 || yaysNotSender != yaysSender3) &&
            (length < 5 || yaysNotSender != yaysSender4);
    mathint approvalsYaysSender0Before = approvals(yaysSender0);
    mathint approvalsYaysSender1Before = approvals(yaysSender1);
    mathint approvalsYaysSender2Before = approvals(yaysSender2);
    mathint approvalsYaysSender3Before = approvals(yaysSender3);
    mathint approvalsYaysSender4Before = approvals(yaysSender4);
    mathint approvalsYaysNotSenderBefore = approvals(yaysNotSender);
    mathint depositsSenderBefore = deposits(e.msg.sender);
    mathint depositsOtherBefore = deposits(otherAddr);
    mathint lastBefore = last(anyAddr);

    free(e, wad);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsYaysSender0After = approvals(yaysSender0);
    mathint approvalsYaysSender1After = approvals(yaysSender1);
    mathint approvalsYaysSender2After = approvals(yaysSender2);
    mathint approvalsYaysSender3After = approvals(yaysSender3);
    mathint approvalsYaysSender4After = approvals(yaysSender4);
    mathint approvalsYaysNotSenderAfter = approvals(yaysNotSender);
    mathint depositsSenderAfter = deposits(e.msg.sender);
    mathint depositsOtherAfter = deposits(otherAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == liveBefore, "free did not keep unchanged live";
    assert hatAfter == hatBefore, "free did not keep unchanged hat";
    assert slatesAfter == slatesBefore, "free did not keep unchanged every slates[x][y]";
    assert votesAfter == votesBefore, "free did not keep unchanged every votes[x]";
    assert length >= 1 => approvalsYaysSender0After == approvalsYaysSender0Before - wad, "free did not decrease approvals[yaysSender0] by wad";
    assert length >= 2 => approvalsYaysSender1After == approvalsYaysSender1Before - wad, "free did not decrease approvals[yaysSender1] by wad";
    assert length >= 3 => approvalsYaysSender2After == approvalsYaysSender2Before - wad, "free did not decrease approvals[yaysSender2] by wad";
    assert length >= 4 => approvalsYaysSender3After == approvalsYaysSender3Before - wad, "free did not decrease approvals[yaysSender3] by wad";
    assert length == 5 => approvalsYaysSender4After == approvalsYaysSender4Before - wad, "free did not decrease approvals[yaysSender4] by wad";
    assert approvalsYaysNotSenderAfter == approvalsYaysNotSenderBefore, "free did not keep unchanged the rest of approvals[x]";
    assert depositsSenderAfter == depositsSenderBefore - wad, "free did not decrease deposits[sender] by wad";
    assert depositsOtherAfter == depositsOtherBefore, "free did not keep unchanged the rest of deposits[x]";
    assert lastAfter == lastBefore, "free did not keep unchanged last[x]";
}

// Verify revert rules on free
rule free_revert(uint256 wad) {
    env e;

    require maxYays() == 5;
    require gov.balanceOf(currentContract) >= wad;
    require gov.balanceOf(e.msg.sender) + wad < max_uint256;
    address addr0 = 0;
    require e.msg.sender != addr0 && e.msg.sender != gov;

    mathint lastSender = last(e.msg.sender);
    mathint depositsSender = deposits(e.msg.sender);
    bytes32 votesSender = votes(e.msg.sender);
    uint256 length = length(votesSender);
    require length <= maxYays();
    address yaysSender0 = length >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address yaysSender1 = length >= 2 ? slates(votesSender, 1) : addr0;
    address yaysSender2 = length >= 3 ? slates(votesSender, 2) : addr0;
    address yaysSender3 = length >= 4 ? slates(votesSender, 3) : addr0;
    address yaysSender4 = length == 5 ? slates(votesSender, 4) : addr0;
    require length <= 1 || yaysSender1 > yaysSender0;
    require length <= 2 || yaysSender2 > yaysSender1;
    require length <= 3 || yaysSender3 > yaysSender2;
    require length <= 4 || yaysSender4 > yaysSender3;
    mathint app0 = approvals(yaysSender0);
    mathint app1 = approvals(yaysSender1);
    mathint app2 = approvals(yaysSender2);
    mathint app3 = approvals(yaysSender3);
    mathint app4 = approvals(yaysSender4);

    free@withrevert(e, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = to_mathint(e.block.number) <= lastSender;
    bool revert3 = depositsSender < to_mathint(wad);
    bool revert4 = length >= 1 && app0 < to_mathint(wad);
    bool revert5 = length >= 2 && app1 < to_mathint(wad);
    bool revert6 = length >= 3 && app2 < to_mathint(wad);
    bool revert7 = length >= 4 && app3 < to_mathint(wad);
    bool revert8 = length == 5 && app4 < to_mathint(wad);

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert revert6 => lastReverted, "revert6 failed";
    assert revert7 => lastReverted, "revert7 failed";
    assert revert8 => lastReverted, "revert8 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5 || revert6 ||
                           revert7 || revert8, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting etch
rule etch(address[] yays) {
    env e;

    require maxYays() == 5;

    uint256 anyUint;
    address anyAddr;

    bytes32 slateYays = yays.length <= 5 ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    bytes32 otherB32;
    require otherB32 != slateYays;
    require length(slateYays) <= 5; // Not possible to have an existing array larger than maxYays, but still neeed for prover

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesOtherBefore = slates(otherB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    mathint approvalsBefore = approvals(anyAddr);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last(anyAddr);

    etch(e, yays);

    mathint liveAfter = live();
    address hatAfter = hat();
    address addr0 = 0;
    address slates0After = yays.length >= 1 ? slates(slateYays, 0) : addr0; // Just any addr as it doesn't save it
    address slates1After = yays.length >= 2 ? slates(slateYays, 1) : addr0;
    address slates2After = yays.length >= 3 ? slates(slateYays, 2) : addr0;
    address slates3After = yays.length >= 4 ? slates(slateYays, 3) : addr0;
    address slates4After = yays.length == 5 ? slates(slateYays, 4) : addr0;
    address slatesOtherAfter = slates(otherB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsAfter = approvals(anyAddr);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == liveBefore, "etch did not keep unchanged live";
    assert hatAfter == hatBefore, "etch did not keep unchanged hat";
    assert yays.length >= 1 => slates0After == yays[0], "etch did not set slates[slateYays][0] as yays[0]";
    assert yays.length >= 2 => slates1After == yays[1], "etch did not set slates[slateYays][1] as yays[1]";
    assert yays.length >= 3 => slates2After == yays[2], "etch did not set slates[slateYays][2] as yays[2]";
    assert yays.length >= 4 => slates3After == yays[3], "etch did not set slates[slateYays][3] as yays[3]";
    assert yays.length == 5 => slates4After == yays[4], "etch did not set slates[slateYays][4] as yays[4]";
    assert slatesOtherAfter == slatesOtherBefore, "etch did not keep unchanged the rest of slates[x][y]";
    assert votesAfter == votesBefore, "etch did not keep unchanged every votes[x]";
    assert approvalsAfter == approvalsBefore, "etch did not keep unchanged every approvals[x]";
    assert depositsAfter == depositsBefore, "etch did not keep unchanged every deposits[x]";
    assert lastAfter == lastBefore, "etch did not keep unchanged every last[x]";
}

// Verify revert rules on etch
rule etch_revert(address[] yays) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 slateYays = yays.length <= 5 ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    require length(slateYays) <= 5; // Not possible to have an existing array larger than maxYays, but still neeed for prover

    mathint yaysLength = yays.length;

    etch@withrevert(e, yays);

    bool revert1 = e.msg.value > 0;
    bool revert2 = yaysLength > maxYays;
    bool revert3 = yaysLength >= 2 && yays[0] >= yays[1];
    bool revert4 = yaysLength >= 3 && yays[1] >= yays[2];
    bool revert5 = yaysLength >= 4 && yays[2] >= yays[3];
    bool revert6 = yaysLength == 5 && yays[3] >= yays[4];

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert revert6 => lastReverted, "revert6 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5 || revert6, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting vote
rule vote(bytes32 slate) {
    env e;

    require maxYays() == 5;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    address otherAddr;
    require otherAddr != e.msg.sender;

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesOtherBefore = votes(otherAddr);
    bytes32 votesSenderBefore = votes(e.msg.sender);
    uint256 oldLength = length(votesSenderBefore);
    require oldLength <= maxYays();
    address addr0 = 0;
    address oldYaysSender0 = oldLength >= 1 ? slates(votesSenderBefore, 0) : addr0; // Just any address as placeholder
    address oldYaysSender1 = oldLength >= 2 ? slates(votesSenderBefore, 1) : addr0;
    address oldYaysSender2 = oldLength >= 3 ? slates(votesSenderBefore, 2) : addr0;
    address oldYaysSender3 = oldLength >= 4 ? slates(votesSenderBefore, 3) : addr0;
    address oldYaysSender4 = oldLength == 5 ? slates(votesSenderBefore, 4) : addr0;
    require oldLength <= 1 || oldYaysSender1 > oldYaysSender0;
    require oldLength <= 2 || oldYaysSender2 > oldYaysSender1;
    require oldLength <= 3 || oldYaysSender3 > oldYaysSender2;
    require oldLength <= 4 || oldYaysSender4 > oldYaysSender3;
    uint256 newLength = length(slate);
    require newLength <= maxYays();
    address newYaysSender0 = newLength >= 1 ? slates(slate, 0) : addr0; // Just any address as placeholder
    address newYaysSender1 = newLength >= 2 ? slates(slate, 1) : addr0;
    address newYaysSender2 = newLength >= 3 ? slates(slate, 2) : addr0;
    address newYaysSender3 = newLength >= 4 ? slates(slate, 3) : addr0;
    address newYaysSender4 = newLength == 5 ? slates(slate, 4) : addr0;
    require newLength <= 1 || newYaysSender1 > newYaysSender0;
    require newLength <= 2 || newYaysSender2 > newYaysSender1;
    require newLength <= 3 || newYaysSender3 > newYaysSender2;
    require newLength <= 4 || newYaysSender4 > newYaysSender3;
    address yaysNotSender;
    require (oldLength < 1 || yaysNotSender != oldYaysSender0) &&
            (oldLength < 2 || yaysNotSender != oldYaysSender1) &&
            (oldLength < 3 || yaysNotSender != oldYaysSender2) &&
            (oldLength < 4 || yaysNotSender != oldYaysSender3) &&
            (oldLength < 5 || yaysNotSender != oldYaysSender4);
    require (newLength < 1 || yaysNotSender != newYaysSender0) &&
            (newLength < 2 || yaysNotSender != newYaysSender1) &&
            (newLength < 3 || yaysNotSender != newYaysSender2) &&
            (newLength < 4 || yaysNotSender != newYaysSender3) &&
            (newLength < 5 || yaysNotSender != newYaysSender4);
    mathint approvalsOldYaysSender0Before = approvals(oldYaysSender0);
    mathint approvalsOldYaysSender1Before = approvals(oldYaysSender1);
    mathint approvalsOldYaysSender2Before = approvals(oldYaysSender2);
    mathint approvalsOldYaysSender3Before = approvals(oldYaysSender3);
    mathint approvalsOldYaysSender4Before = approvals(oldYaysSender4);
    mathint approvalsNewYaysSender0Before = approvals(newYaysSender0);
    mathint approvalsNewYaysSender1Before = approvals(newYaysSender1);
    mathint approvalsNewYaysSender2Before = approvals(newYaysSender2);
    mathint approvalsNewYaysSender3Before = approvals(newYaysSender3);
    mathint approvalsNewYaysSender4Before = approvals(newYaysSender4);
    mathint approvalsYaysNotSenderBefore = approvals(yaysNotSender);
    mathint depositsSender = deposits(e.msg.sender);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last(anyAddr);

    vote(e, slate);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesSenderAfter = votes(e.msg.sender);
    bytes32 votesOtherAfter = votes(otherAddr);
    mathint approvalsOldYaysSender0After = approvals(oldYaysSender0);
    mathint approvalsOldYaysSender1After = approvals(oldYaysSender1);
    mathint approvalsOldYaysSender2After = approvals(oldYaysSender2);
    mathint approvalsOldYaysSender3After = approvals(oldYaysSender3);
    mathint approvalsOldYaysSender4After = approvals(oldYaysSender4);
    mathint approvalsNewYaysSender0After = approvals(newYaysSender0);
    mathint approvalsNewYaysSender1After = approvals(newYaysSender1);
    mathint approvalsNewYaysSender2After = approvals(newYaysSender2);
    mathint approvalsNewYaysSender3After = approvals(newYaysSender3);
    mathint approvalsNewYaysSender4After = approvals(newYaysSender4);
    mathint approvalsYaysNotSenderAfter = approvals(yaysNotSender);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == liveBefore, "vote did not keep unchanged live";
    assert hatAfter == hatBefore, "vote did not keep unchanged hat";
    assert slatesAfter == slatesBefore, "vote did not keep unchanged every slates[x][y]";
    assert votesSenderAfter == slate, "vote did not set votes[sender] to slate";
    assert votesOtherAfter == votesOtherBefore, "vote did not keep unchanged the rest of votes[x]";
    assert oldLength >= 1 &&
           oldYaysSender0 != newYaysSender0 &&
           oldYaysSender0 != newYaysSender1 &&
           oldYaysSender0 != newYaysSender2 &&
           oldYaysSender0 != newYaysSender3 &&
           oldYaysSender0 != newYaysSender4
           => approvalsOldYaysSender0After == approvalsOldYaysSender0Before - depositsSender, "vote did not decrease approvals[oldYaysSender0] by depositsSender";
    assert oldLength >= 1 &&
           (newLength >= 1 && oldYaysSender0 == newYaysSender0 ||
            newLength >= 2 && oldYaysSender0 == newYaysSender1 ||
            newLength >= 3 && oldYaysSender0 == newYaysSender2 ||
            newLength >= 4 && oldYaysSender0 == newYaysSender3 ||
            newLength == 5 && oldYaysSender0 == newYaysSender4)
           => approvalsOldYaysSender0After == approvalsOldYaysSender0Before, "vote did not keep unchanged approvals[oldYaysSender0]";
    assert oldLength >= 2 &&
           oldYaysSender1 != newYaysSender0 &&
           oldYaysSender1 != newYaysSender1 &&
           oldYaysSender1 != newYaysSender2 &&
           oldYaysSender1 != newYaysSender3 &&
           oldYaysSender1 != newYaysSender4
           => approvalsOldYaysSender1After == approvalsOldYaysSender1Before - depositsSender, "vote did not decrease approvals[oldYaysSender1] by depositsSender";
    assert oldLength >= 2 &&
           (newLength >= 1 && oldYaysSender1 == newYaysSender0 ||
            newLength >= 2 && oldYaysSender1 == newYaysSender1 ||
            newLength >= 3 && oldYaysSender1 == newYaysSender2 ||
            newLength >= 4 && oldYaysSender1 == newYaysSender3 ||
            newLength == 5 && oldYaysSender1 == newYaysSender4)
           => approvalsOldYaysSender1After == approvalsOldYaysSender1Before, "vote did not keep unchanged approvals[oldYaysSender1]";
    assert oldLength >= 3 &&
           oldYaysSender2 != newYaysSender0 &&
           oldYaysSender2 != newYaysSender1 &&
           oldYaysSender2 != newYaysSender2 &&
           oldYaysSender2 != newYaysSender3 &&
           oldYaysSender2 != newYaysSender4
           => approvalsOldYaysSender2After == approvalsOldYaysSender2Before - depositsSender, "vote did not decrease approvals[oldYaysSender2] by depositsSender";
    assert oldLength >= 3 &&
           (newLength >= 1 && oldYaysSender2 == newYaysSender0 ||
            newLength >= 2 && oldYaysSender2 == newYaysSender1 ||
            newLength >= 3 && oldYaysSender2 == newYaysSender2 ||
            newLength >= 4 && oldYaysSender2 == newYaysSender3 ||
            newLength == 5 && oldYaysSender2 == newYaysSender4)
           => approvalsOldYaysSender2After == approvalsOldYaysSender2Before, "vote did not keep unchanged approvals[oldYaysSender2]";
    assert oldLength >= 4 &&
           oldYaysSender3 != newYaysSender0 &&
           oldYaysSender3 != newYaysSender1 &&
           oldYaysSender3 != newYaysSender2 &&
           oldYaysSender3 != newYaysSender3 &&
           oldYaysSender3 != newYaysSender4
           => approvalsOldYaysSender3After == approvalsOldYaysSender3Before - depositsSender, "vote did not decrease approvals[oldYaysSender3] by depositsSender";
    assert oldLength >= 4 &&
           (newLength >= 1 && oldYaysSender3 == newYaysSender0 ||
            newLength >= 2 && oldYaysSender3 == newYaysSender1 ||
            newLength >= 3 && oldYaysSender3 == newYaysSender2 ||
            newLength >= 4 && oldYaysSender3 == newYaysSender3 ||
            newLength == 5 && oldYaysSender3 == newYaysSender4)
           => approvalsOldYaysSender3After == approvalsOldYaysSender3Before, "vote did not keep unchanged approvals[oldYaysSender3]";
    assert oldLength == 5 &&
           oldYaysSender4 != newYaysSender0 &&
           oldYaysSender4 != newYaysSender1 &&
           oldYaysSender4 != newYaysSender2 &&
           oldYaysSender4 != newYaysSender3 &&
           oldYaysSender4 != newYaysSender4
           => approvalsOldYaysSender4After == approvalsOldYaysSender4Before - depositsSender, "vote did not decrease approvals[oldYaysSender4] by depositsSender";
    assert oldLength == 5 &&
           (newLength >= 1 && oldYaysSender4 == newYaysSender0 ||
            newLength >= 2 && oldYaysSender4 == newYaysSender1 ||
            newLength >= 3 && oldYaysSender4 == newYaysSender2 ||
            newLength >= 4 && oldYaysSender4 == newYaysSender3 ||
            newLength == 5 && oldYaysSender4 == newYaysSender4)
           => approvalsOldYaysSender4After == approvalsOldYaysSender4Before, "vote did not keep unchanged approvals[oldYaysSender4]";
    assert newLength >= 1 &&
           newYaysSender0 != oldYaysSender0 &&
           newYaysSender0 != oldYaysSender1 &&
           newYaysSender0 != oldYaysSender2 &&
           newYaysSender0 != oldYaysSender3 &&
           newYaysSender0 != oldYaysSender4
           => approvalsNewYaysSender0After == approvalsNewYaysSender0Before + depositsSender, "vote did not increase approvals[newYaysSender0] by depositsSender";
    assert newLength >= 2 &&
           newYaysSender1 != oldYaysSender0 &&
           newYaysSender1 != oldYaysSender1 &&
           newYaysSender1 != oldYaysSender2 &&
           newYaysSender1 != oldYaysSender3 &&
           newYaysSender1 != oldYaysSender4
           => approvalsNewYaysSender1After == approvalsNewYaysSender1Before + depositsSender, "vote did not increase approvals[newYaysSender1] by depositsSender";
    assert newLength >= 3 &&
           newYaysSender2 != oldYaysSender0 &&
           newYaysSender2 != oldYaysSender1 &&
           newYaysSender2 != oldYaysSender2 &&
           newYaysSender2 != oldYaysSender3 &&
           newYaysSender2 != oldYaysSender4
           => approvalsNewYaysSender2After == approvalsNewYaysSender2Before + depositsSender, "vote did not increase approvals[newYaysSender2] by depositsSender";
    assert newLength >= 4 &&
           newYaysSender3 != oldYaysSender0 &&
           newYaysSender3 != oldYaysSender1 &&
           newYaysSender3 != oldYaysSender2 &&
           newYaysSender3 != oldYaysSender3 &&
           newYaysSender3 != oldYaysSender4
           => approvalsNewYaysSender3After == approvalsNewYaysSender3Before + depositsSender, "vote did not increase approvals[newYaysSender3] by depositsSender";
    assert newLength == 5 &&
           newYaysSender4 != oldYaysSender0 &&
           newYaysSender4 != oldYaysSender1 &&
           newYaysSender4 != oldYaysSender2 &&
           newYaysSender4 != oldYaysSender3 &&
           newYaysSender4 != oldYaysSender4
           => approvalsNewYaysSender4After == approvalsNewYaysSender4Before + depositsSender, "vote did not increase approvals[newYaysSender4] by depositsSender";
    assert approvalsYaysNotSenderAfter == approvalsYaysNotSenderBefore, "vote did not keep unchanged the rest of approvals[x]";
    assert depositsAfter == depositsBefore, "vote did not keep unchanged every deposits[x]";
    assert lastAfter == lastBefore, "vote did not keep unchanged every last[x]";
}

// Verify correct storage changes for non reverting launch
rule lift(address whom) {
    env e;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    mathint liveBefore = live();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    mathint approvalsBefore = approvals(anyAddr);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last(anyAddr);

    lift(e, whom);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsAfter = approvals(anyAddr);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == liveBefore, "lift did not keep unchanged live";
    assert hatAfter == whom, "lift did not set hat to whom";
    assert slatesAfter == slatesBefore, "lift did not keep unchanged every slates[x][y]";
    assert votesAfter == votesBefore, "lift did not keep unchanged every votes[x]";
    assert approvalsAfter == approvalsBefore, "lift did not keep unchanged every approvals[x]";
    assert depositsAfter == depositsBefore, "lift did not keep unchanged every deposits[x]";
    assert lastAfter == lastBefore, "lift did not keep unchanged every last[x]";
}

// Verify revert rules on lift
rule lift_revert(address whom) {
    env e;

    address hat = hat();
    mathint approvalsWhom = approvals(whom);
    mathint approvalsHat = approvals(hat);

    lift@withrevert(e, whom);

    bool revert1 = e.msg.value > 0;
    bool revert2 = approvalsWhom <= approvalsHat;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert lastReverted => revert1 || revert2, "Revert rules are not covering all the cases";
}
