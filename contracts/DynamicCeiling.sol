pragma solidity ^0.4.11;

/*
    Copyright 2017, Jordi Baylina

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/// @title DynamicCeiling Contract
/// @author Jordi Baylina
/// @dev This contract calculates the ceiling from a series of curves.
///  These curves are committed first and revealed later.
///  All the curves must be in increasing order and the last curve is marked
///  as the last one.
///  This contract allows to hide and reveal the ceiling at will of the owner.


import "./SafeMath.sol";
import "./Ownable.sol";
import "./CeilingStrategy.sol";

contract DynamicCeiling is CeilingStrategy, Ownable {
    using SafeMath for uint;

    struct Curve {
        bytes32 hash;
        // Absolute limit for this curve
        uint limit;
        // The funds remaining to be collected are divided by `slopeFactor` smooth ceiling
        // with a long tail where big and small buyers can take part.
        uint slopeFactor;
        // This keeps the curve flat at this number, until funds to be collected is less than this
        uint collectMinimum;
    }

    Curve[] public curves;
    uint public currentIndex;
    uint public revealedCurves;
    bool public allRevealed;


    function DynamicCeiling(address _owner) {
        owner = _owner;
    }

    /// @notice This should be called by the creator of the contract to commit
    ///  all the curves.
    /// @param _curveHashes Array of hashes of each curve. Each hash is calculated
    ///  by the `calculateHash` method. More hashes than actual curves can be
    ///  committed in order to hide also the number of curves.
    ///  The remaining hashes can be just random numbers.
    function setHiddenCurves(bytes32[] _curveHashes) public onlyOwner {
        require(curves.length == 0);

        curves.length = _curveHashes.length;
        for (uint i = 0; i < _curveHashes.length; i = i.add(1)) {
            curves[i].hash = _curveHashes[i];
        }
    }


    /// @notice Anybody can reveal the next curve if he knows it.
    /// @param _limit Ceiling cap.
    ///  (must be greater or equal to the previous one).
    /// @param _last `true` if it's the last curve.
    /// @param _salt Random number used to commit the curve
    function revealCurve(uint _limit, uint _slopeFactor, uint _collectMinimum,
                         bool _last, bytes32 _salt) public {
        require(!allRevealed);

        require(curves[revealedCurves].hash == calculateHash(_limit, _slopeFactor, _collectMinimum,
                                                             _last, _salt));

        require(_limit != 0 && _slopeFactor != 0 && _collectMinimum != 0);
        if (revealedCurves > 0) {
            require(_limit >= curves[revealedCurves.sub(1)].limit);
        }

        curves[revealedCurves].limit = _limit;
        curves[revealedCurves].slopeFactor = _slopeFactor;
        curves[revealedCurves].collectMinimum = _collectMinimum;
        revealedCurves = revealedCurves.add(1);

        if (_last) allRevealed = true;
    }

    /// @notice Reveal multiple curves at once
    function revealMulti(uint[] _limits, uint[] _slopeFactors, uint[] _collectMinimums,
                         bool[] _lasts, bytes32[] _salts) public {
        // Do not allow none and needs to be same length for all parameters
        require(_limits.length != 0 &&
                _limits.length == _slopeFactors.length &&
                _limits.length == _collectMinimums.length &&
                _limits.length == _lasts.length &&
                _limits.length == _salts.length);

        for (uint i = 0; i < _limits.length; i = i.add(1)) {
            revealCurve(_limits[i], _slopeFactors[i], _collectMinimums[i],
                        _lasts[i], _salts[i]);
        }
    }

    /// @notice Move to curve, used as a failsafe
    function moveTo(uint _index) public onlyOwner {
        require(_index < revealedCurves &&       // No more curves
                _index == currentIndex.add(1));  // Only move one index at a time
        currentIndex = _index;
    }

    /// @return Return the funds to collect for the current point on the curve
    ///  (or 0 if no curves revealed yet)
    function toCollect(uint collected) public returns (uint) {
        if (revealedCurves == 0) return 0;

        // Move to the next curve
        if (collected >= curves[currentIndex].limit) {  // Catches `limit == 0`
            uint nextIndex = currentIndex.add(1);
            if (nextIndex >= revealedCurves) return 0;  // No more curves
            currentIndex = nextIndex;
            if (collected >= curves[currentIndex].limit) return 0;  // Catches `limit == 0`
        }

        // Everything left to collect from this limit
        uint difference = curves[currentIndex].limit.sub(collected);

        // Current point on the curve
        uint collect = difference.div(curves[currentIndex].slopeFactor);

        // Prevents paying too much fees vs to be collected; breaks long tail
        if (collect <= curves[currentIndex].collectMinimum) {
            if (difference > curves[currentIndex].collectMinimum) {
                return curves[currentIndex].collectMinimum;
            } else {
                return difference;
            }
        } else {
            return collect;
        }
    }

    /// @notice Calculates the hash of a curve.
    /// @param _limit Ceiling cap.
    /// @param _last `true` if it's the last curve.
    /// @param _salt Random number that will be needed to reveal this curve.
    /// @return The calculated hash of this curve to be used in the `setHiddenCurves` method
    function calculateHash(uint _limit, uint _slopeFactor, uint _collectMinimum,
                           bool _last, bytes32 _salt) public constant returns (bytes32) {
        return keccak256(_limit, _slopeFactor, _collectMinimum, _last, _salt);
    }

    /// @return Return the total number of curves committed
    ///  (can be larger than the number of actual curves on the curve to hide
    ///  the real number of curves)
    function nCurves() public constant returns (uint) {
        return curves.length;
    }

    function weiAllowedToReceive(uint _value, uint _weiRaised) public constant returns (uint) {
        uint weiToCollect = toCollect(_weiRaised);

        uint amount;

        if (_value <= weiToCollect) {
            amount = _value;
        } else {
            amount = weiToCollect;
        }

        return amount;
    }

    function isCrowdsaleFull(uint _weiRaised) public constant returns (bool) {
        return toCollect(_weiRaised) == 0 && allRevealed;
    }

}