package buildui.connectors;
/*
 * Copyright (c) 2002-2006 University of Utah and the Flux Group.
 * All rights reserved.
 * This file is part of the Emulab network testbed software.
 * 
 * Emulab is free software, also known as "open source;" you can
 * redistribute it and/or modify it under the terms of the GNU Affero
 * General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 * 
 * Emulab is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
 * more details, which can be found in the file AGPL-COPYING at the root of
 * the source tree.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
import java.awt.*;

import buildui.paint.Element;
import buildui.paint.PropertiesArea;


public class EmulatedConnection extends Connection {

	private static Color paleBlue;

	static {
		paleBlue = new Color(0.8f, 0.8f, 1.0f);
	}

	public void drawIcon(Graphics g) {
		g.setColor(Color.lightGray);
		g.fillRect(-6, -6, 16, 16);

		g.setColor(paleBlue);
		g.fillRect(-8, -8, 16, 16);

		g.setColor(Color.black);
		g.drawRect(-8, -8, 16, 16);
	}

	public EmulatedConnection(String newName, Element na, Element nb) {
		super(newName, na, nb);
	}

  static PropertiesArea propertiesArea = new EmulatedConnectionPropertiesArea() ;

  public PropertiesArea getPropertiesArea() {
    return propertiesArea ;
  }

}
